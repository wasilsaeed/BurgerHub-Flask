from flask import Blueprint, render_template, request, redirect, url_for, flash, session

from app import db
from app.models import Product, OrderItem, Order

main = Blueprint("main", __name__)


# ====================
## HOME PAGE ROUTE
# ====================

@main.route("/")
def home():
    # featured_products = [product for product in products if product["is_featured"]]
    featured_products = Product.query.filter_by(
        is_available = True,
        is_featured = True
    ).limit(4).all()
    return render_template('index.html', featured_products=featured_products)

# ====================
## MENU PAGE ROUTE
# ====================

@main.route("/menu")
def menu():
    products = Product.query.filter_by(
        is_available=True
    ).order_by(
        Product.created_at.desc()
    ).all()
    return render_template("menu.html", products=products)

# ====================
## PRODUCT DETAILS ROUTE
# ====================

@main.route("/product/<int:product_id>")
def product_detail(product_id):
    # product = next((item for item in products if item["id"] == product_id), None)
    product = Product.query.get_or_404(product_id)
    return render_template("product_detail.html", product=product)

# ====================
## ADD PRODUCT ROUTE
# ====================

@main.route("/admin/products/add", methods=["GET", "POST"])
def add_product():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        category = request.form.get("category", "").strip()
        price = request.form.get("price", "").strip()
        image = request.form.get("image", "").strip()
        description = request.form.get("description", "").strip()
        is_featured = request.form.get("is_featured") == "on"
        is_available = request.form.get("is_available") == "on"

        if not name or not category or not price or not description:
            flash("Please fill in all required fields.", "error")
            return redirect(url_for("main.add_product"))

        try:
            price = int(price)
        except ValueError:
            flash("Price must be a valid number.", "error")
            return redirect(url_for("main.add_product"))

        product = Product(
            name=name,
            category=category,
            price=price,
            image=image,
            description=description,
            is_featured=is_featured,
            is_available=is_available,
        )

        db.session.add(product)
        db.session.commit()

        flash("Product added successfully.", "success")
        return redirect(url_for("main.menu"))

    return render_template("add_product.html")

# ====================
## ADD TO CART ROUTE
# ====================

@main.route("/add_to_cart/<int:product_id>", methods=["POST"])
def add_to_cart(product_id):
    product = Product.query.get_or_404(product_id)

    if not product.is_available:
        flash("This product is currently unavailable.", "warning")
        return redirect(request.referrer or url_for('menu'))

    cart = session.get("cart", {})

    product_id = str(product_id)

    if product_id in cart:
        cart[product_id] += 1
    else:
        cart[product_id] = 1

    session["cart"] = cart
    session.modified = True

    flash(f"{product.name} added to cart.", "success")
    return redirect(request.referrer or url_for("menu"))



# =====================
## CART ROUTES
# =====================

def get_cart_items():
    cart = session.get("cart", {})

    cart_items = []
    cart_total = 0

    for product_id, quantity in cart.items():
        product = Product.query.get(int(product_id))

        if product:
            item_total = product.price * quantity
            cart_total += item_total

            cart_items.append({
                "product": product,
                "quantity": quantity,
                "item_total": item_total
            })

    return cart_items, cart_total


@main.route("/cart")
def cart():
    cart_items, cart_total = get_cart_items()

    return render_template(
        "cart.html",
        cart_items=cart_items,
        cart_total=cart_total
    )

@main.route("/update_cart/<int:product_id>", methods=["POST"])
def update_cart(product_id):
    quantity = int(request.form.get("quantity", 1))

    cart = session.get("cart", {})
    product_id = str(product_id)

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

    if product_id in cart:
        cart.pop(product_id)

    session["cart"] = cart
    session.modified = True

    flash("Product removed from cart.", "info")
    return redirect(url_for("main.cart"))

@main.route("/clear-cart", methods=["POST"])
def clear_cart():
    session.pop("cart", None)

    flash("Cart cleared.", "info")
    return redirect(url_for("main.cart"))

# =====================
## CHECKOUT ROUTE
# =====================

@main.route("/checkout")
def checkout():
    cart_items, cart_total = get_cart_items()

    if not cart_items:
        return render_template(
            "checkout.html",
            cart_items=cart_items,
            cart_total=cart_total
        )

    return render_template(
        "checkout.html",
        cart_items=cart_items,
        cart_total=cart_total
    )


# ====================
## PLACE ORDER ROUTE
# ===================
@main.route("/place-order", methods=["GET", "POST"])
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

    order = Order(
        customer_name=customer_name,
        customer_phone=customer_phone,
        customer_address=customer_address,
        payment_method=payment_method,
        total_amount=cart_total,
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

    db.session.commit()

    session.pop("cart", None)

    flash("Your order has been placed successfully.", "success")
    return redirect(url_for("main.checkout_success", order_id=order.id))


# ====================
## CHECKOUT SUCCESS ROUTE
# ====================

@main.route("/checkout-success/<int:order_id>")
def checkout_success(order_id):
    order = Order.query.get_or_404(order_id)

    return render_template(
        "checkout_success.html",
        order=order
    )


# ====================
## ABOUT ROUTE
# ====================

@main.route("/about")
def about():
    return render_template("about.html")

# ====================
## CONTACT ROUTE
# ====================

@main.route("/contact")
def contact():
    return render_template("contact.html")