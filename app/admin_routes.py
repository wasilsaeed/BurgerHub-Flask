from flask import Blueprint, render_template, redirect, url_for, request, flash

from app import db
from app.models import Product, Order

admin = Blueprint("admin", __name__, url_prefix="/admin")


@admin.route("/")
@admin.route("/dashboard")
def dashboard():
    products_count = Product.query.count()
    available_count = Product.query.filter_by(is_available=True).count()
    featured_count = Product.query.filter_by(is_featured=True).count()
    orders_count = Order.query.count()

    recent_products = Product.query.order_by(Product.id.desc()).limit(5).all()
    recent_orders = Order.query.order_by(Order.id.desc()).limit(5).all()

    return render_template(
        "admin/dashboard.html",
        count=products_count,
        available_count=available_count,
        featured_count=featured_count,
        orders_count=orders_count,
        recent_products=recent_products,
        recent_orders=recent_orders
    )


@admin.route("/products")
def products():
    products = Product.query.order_by(Product.id.desc()).all()
    return render_template("admin/products.html", products=products)
@admin.route("/products/add", methods=["POST"])
def add_product():
    name = request.form.get("name", "").strip()
    category = request.form.get("category", "").strip()
    price = request.form.get("price", "").strip()
    image = request.form.get("image", "").strip()
    description = request.form.get("description", "").strip()
    is_featured = request.form.get("is_featured") == "on"
    is_available = request.form.get("is_available") == "on"

    if not name or not category or not price or not description:
        flash("Please fill in all required fields.", "error")
        return redirect(url_for("admin.products"))

    try:
        price = float(price)
    except ValueError:
        flash("Price must be a valid number.", "error")
        return redirect(url_for("admin.products"))

    product = Product(
        name=name,
        category=category,
        price=price,
        image=image,
        description=description,
        is_featured=is_featured,
        is_available=is_available
    )

    db.session.add(product)
    db.session.commit()

    flash("Product added successfully.", "success")
    return redirect(url_for("admin.products"))


@admin.route("/products/edit/<int:product_id>", methods=["GET", "POST"])
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)

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
            return redirect(url_for("admin.edit_product", product_id=product.id))

        try:
            price = float(price)
        except ValueError:
            flash("Price must be a valid number.", "error")
            return redirect(url_for("admin.edit_product", product_id=product.id))

        product.name = name
        product.category = category
        product.price = price
        product.image = image
        product.description = description
        product.is_featured = is_featured
        product.is_available = is_available

        db.session.commit()

        flash("Product updated successfully.", "success")
        return redirect(url_for("admin.products"))

    return render_template("admin/edit_product.html", product=product)


@admin.route("/products/delete/<int:product_id>", methods=["POST"])
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)

    db.session.delete(product)
    db.session.commit()

    flash("Product deleted successfully.", "success")
    return redirect(url_for("admin.products"))


@admin.route("/orders")
def orders():
    orders = Order.query.order_by(Order.id.desc()).all()

    pending_count = Order.query.filter_by(status="Pending").count()
    preparing_count = Order.query.filter_by(status="Preparing").count()
    delivered_count = Order.query.filter_by(status="Delivered").count()

    return render_template(
        "admin/orders.html",
        orders=orders,
        pending_count=pending_count,
        preparing_count=preparing_count,
        delivered_count=delivered_count
    )


@admin.route("/customers")
def customers():
    orders = Order.query.order_by(Order.id.desc()).all()

    customers = {}

    for order in orders:
        key = order.customer_phone

        if key not in customers:
            customers[key] = {
                "name": order.customer_name,
                "phone": order.customer_phone,
                "address": order.customer_address,
                "orders": 0,
                "spent": 0
            }

        customers[key]["orders"] += 1
        customers[key]["spent"] += order.total_amount or 0

    return render_template(
        "admin/customers.html",
        customers=customers.values()
    )


@admin.route("/settings", methods=["GET", "POST"])
def settings():
    if request.method == "POST":
        flash("Settings updated successfully.", "success")
        return redirect(url_for("admin.settings"))

    return render_template("admin/settings.html")