from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
import secrets
import math

from app import db
from app.models import Product, OrderItem, Order, ContactMessage, DiscountCode


main = Blueprint("main", __name__)


DISCOUNT_PERCENTAGE = 0.20


def calculate_discount(cart_total):
    discount_amount = math.floor(cart_total * DISCOUNT_PERCENTAGE)
    final_total = math.floor(cart_total - discount_amount)

    return discount_amount, final_total


@main.route("/", methods=["GET"])
def home():
    items_count = Product.query.count()

    featured_products = Product.query.filter_by(
        is_available=True,
        is_featured=True
    ).limit(4).all()

    return render_template(
        "index.html",
        featured_products=featured_products,
        count=items_count
    )


@main.route("/claim-discount", methods=["POST"])
def claim_discount():
    email = request.form.get("email", "").strip().lower()

    if not email:
        return jsonify({
            "success": False,
            "message": "Email is required."
        }), 400

    code = "BURGER-" + secrets.token_hex(3).upper()

    discount = DiscountCode(
        email=email,
        code=code,
        used=False
    )

    db.session.add(discount)
    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Discount claimed successfully!",
        "code": code
    })


@main.route("/menu")
def menu():
    products = Product.query.filter_by(
        is_available=True
    ).order_by(
        Product.created_at.desc()
    ).all()

    return render_template("menu.html", products=products)


@main.route("/product/<int:product_id>")
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)

    if not product.is_available:
        flash("This product is currently unavailable.", "warning")
        return redirect(url_for("main.menu"))

    return render_template("product_detail.html", product=product)


@main.route("/add-to-cart/<int:product_id>", methods=["POST"])
def add_to_cart(product_id):
    product = Product.query.get_or_404(product_id)

    if not product.is_available:
        flash("This product is currently unavailable.", "warning")
        return redirect(request.referrer or url_for("main.menu"))

    cart = session.get("cart", {})
    product_id = str(product_id)

    cart[product_id] = cart.get(product_id, 0) + 1

    session["cart"] = cart
    session.modified = True

    flash(f"{product.name} added to cart.", "success")
    return redirect(request.referrer or url_for("main.menu"))


def get_cart_items():
    cart = session.get("cart", {})
    cart_items = []
    cart_total = 0

    for product_id, quantity in cart.items():
        try:
            product_id = int(product_id)
            quantity = int(quantity)
        except ValueError:
            continue

        product = Product.query.get(product_id)

        if product and product.is_available and quantity > 0:
            item_total = product.price * quantity
            cart_total += item_total

            cart_items.append({
                "product": product,
                "quantity": quantity,
                "item_total": item_total
            })

    return cart_items, cart_total


def get_valid_discount():
    discount_code = session.get("discount_code")

    if not discount_code:
        return None, None

    discount = DiscountCode.query.filter_by(
        code=discount_code,
        used=False
    ).first()

    if not discount:
        session.pop("discount_code", None)
        return None, None

    return discount, discount_code


@main.route("/cart")
def cart():
    cart_items, cart_total = get_cart_items()

    discount, discount_code = get_valid_discount()
    discount_amount = 0
    final_total = math.floor(cart_total)

    if discount:
        discount_amount, final_total = calculate_discount(cart_total)

    return render_template(
        "cart.html",
        cart_items=cart_items,
        cart_total=cart_total,
        discount_code=discount_code,
        discount_amount=discount_amount,
        final_total=final_total
    )


@main.route("/update-cart/<int:product_id>", methods=["POST"])
def update_cart(product_id):
    cart = session.get("cart", {})
    product_id = str(product_id)

    try:
        quantity = int(request.form.get("quantity", 1))
    except ValueError:
        quantity = 1

    if product_id in cart:
        if quantity <= 0:
            cart.pop(product_id)
        else:
            cart[product_id] = quantity

    session["cart"] = cart
    session.modified = True

    flash("Cart updated successfully.", "success")
    return redirect(url_for("main.cart"))


@main.route("/remove-from-cart/<int:product_id>", methods=["POST"])
def remove_from_cart(product_id):
    cart = session.get("cart", {})
    product_id = str(product_id)

    cart.pop(product_id, None)

    session["cart"] = cart
    session.modified = True

    flash("Product removed from cart.", "info")
    return redirect(url_for("main.cart"))


@main.route("/clear-cart", methods=["POST"])
def clear_cart():
    session.pop("cart", None)
    session.pop("discount_code", None)

    flash("Cart cleared.", "info")
    return redirect(url_for("main.cart"))


@main.route("/cart/apply-discount", methods=["POST"])
def apply_cart_discount():
    code = request.form.get("discount_code", "").strip().upper()

    if not code:
        flash("Please enter a discount code.", "danger")
        return redirect(url_for("main.cart"))

    discount = DiscountCode.query.filter_by(
        code=code,
        used=False
    ).first()

    if not discount:
        session.pop("discount_code", None)
        flash("Invalid or already used discount code.", "danger")
        return redirect(url_for("main.cart"))

    session["discount_code"] = code
    session.modified = True

    flash("Discount code applied successfully.", "success")
    return redirect(url_for("main.cart"))


@main.route("/cart/remove-discount", methods=["POST"])
def remove_cart_discount():
    session.pop("discount_code", None)
    flash("Discount code removed.", "success")

    return redirect(url_for("main.cart"))


@main.route("/checkout")
def checkout():
    cart_items, cart_total = get_cart_items()

    if not cart_items:
        flash("Your cart is empty.", "warning")
        return redirect(url_for("main.cart"))

    discount, discount_code = get_valid_discount()
    discount_amount = 0
    final_total = math.floor(cart_total)

    if discount:
        discount_amount, final_total = calculate_discount(cart_total)

    return render_template(
        "checkout.html",
        cart_items=cart_items,
        cart_total=cart_total,
        discount_code=discount_code,
        discount_amount=discount_amount,
        final_total=final_total
    )


@main.route("/place-order", methods=["POST"])
def place_order():
    cart_items, cart_total = get_cart_items()

    if not cart_items:
        flash("Your cart is empty.", "warning")
        return redirect(url_for("main.cart"))

    customer_name = request.form.get("customer_name", "").strip()
    customer_phone = request.form.get("customer_phone", "").strip()
    customer_address = request.form.get("customer_address", "").strip()
    payment_method = request.form.get("payment_method", "cash_on_delivery")

    if not customer_name or not customer_phone or not customer_address:
        flash("Please fill in all required fields.", "danger")
        return redirect(url_for("main.checkout"))

    discount, discount_code = get_valid_discount()
    discount_amount = 0
    final_total = math.floor(cart_total)

    if discount:
        discount_amount, final_total = calculate_discount(cart_total)

    order = Order(
        customer_name=customer_name,
        customer_phone=customer_phone,
        customer_address=customer_address,
        payment_method=payment_method,
        total_amount=final_total,
        status="Pending"
    )

    db.session.add(order)
    db.session.flush()

    for item in cart_items:
        product = item["product"]

        order_item = OrderItem(
            order_id=order.id,
            product_id=product.id,
            product_name=product.name,
            product_price=product.price,
            quantity=item["quantity"],
            item_total=item["item_total"]
        )

        db.session.add(order_item)

    if discount:
        discount.used = True

    db.session.commit()

    session.pop("cart", None)
    session.pop("discount_code", None)

    flash("Your order has been placed successfully.", "success")
    return redirect(url_for("main.checkout_success", order_id=order.id))


@main.route("/checkout-success/<int:order_id>")
def checkout_success(order_id):
    order = Order.query.get_or_404(order_id)

    return render_template(
        "checkout_success.html",
        order=order
    )


@main.route("/about")
def about():
    return render_template("about.html")


@main.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        message = request.form.get("message", "").strip()

        if not name or not email or not message:
            flash("All fields are required.", "warning")
            return redirect(url_for("main.contact"))

        contact_message = ContactMessage(
            name=name,
            email=email,
            message=message
        )

        db.session.add(contact_message)
        db.session.commit()

        flash("Thank you for contacting us. We will get back to you soon.", "success")
        return redirect(url_for("main.contact"))

    return render_template("contact.html")


@main.route("/privacy")
def privacy():
    return render_template("privacy_policy.html")


@main.route("/terms")
def terms():
    return render_template("terms_of_service.html")


@main.route("/track-order", methods=["GET", "POST"])
def track_order():
    order = None

    if request.method == "POST":
        order_id = request.form.get("order_id", "").strip()
        customer_phone = request.form.get("customer_phone", "").strip()

        if not order_id or not customer_phone:
            flash("Please enter your order ID and phone number.", "warning")
            return redirect(url_for("main.track_order"))

        order = Order.query.filter_by(
            id=order_id,
            customer_phone=customer_phone
        ).first()

        if not order:
            flash("No order found with these details.", "danger")

    return render_template("track_order.html", order=order)