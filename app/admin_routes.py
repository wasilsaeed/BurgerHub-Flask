from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from sqlalchemy import func
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash


from app import db
from app.models import Product, Order, SiteSetting

admin = Blueprint("admin", __name__, url_prefix="/admin")


ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"


def admin_login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not session.get("admin_logged_in"):
            flash("Please login to access admin dashboard.", "warning")
            return redirect(url_for("admin.login"))
        return func(*args, **kwargs)
    return wrapper


@admin.route("/login", methods=["GET", "POST"])
def login():
    if session.get("admin_logged_in"):
        return redirect(url_for("admin.dashboard"))

    setting = SiteSetting.query.first()

    if not setting:
        setting = SiteSetting(
            admin_username="admin",
            admin_password_hash=generate_password_hash("admin123")
        )
        db.session.add(setting)
        db.session.commit()

    if not setting.admin_password_hash:
        setting.admin_password_hash = generate_password_hash("admin123")
        db.session.commit()

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        if (
            username == setting.admin_username
            and check_password_hash(setting.admin_password_hash, password)
        ):
            session["admin_logged_in"] = True
            flash("Welcome back, Admin.", "success")
            return redirect(url_for("admin.dashboard"))

        flash("Invalid username or password.", "danger")

    return render_template("admin/login.html")


@admin.route("/logout")
def logout():
    session.pop("admin_logged_in", None)
    flash("You have been logged out.", "info")
    return redirect(url_for("admin.login"))

@admin.route("/")
@admin.route("/dashboard")
@admin_login_required
def dashboard():
    total_products = Product.query.count()
    total_orders = Order.query.count()

    total_revenue = db.session.query(
        func.coalesce(func.sum(Order.total_amount), 0)
    ).scalar()

    total_customers = db.session.query(
        func.count(func.distinct(Order.customer_phone))
    ).scalar()

    recent_orders = Order.query.order_by(Order.id.desc()).limit(5).all()

    return render_template(
        "admin/dashboard.html",
        total_products=total_products,
        total_orders=total_orders,
        total_revenue=total_revenue,
        total_customers=total_customers,
        recent_orders=recent_orders
    )

@admin.route("/products")
@admin_login_required
def products():
    products = Product.query.order_by(Product.id.desc()).all()
    return render_template("admin/products.html", products=products)

@admin.route("/products/add", methods=["POST"])
@admin_login_required
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
        is_available=is_available,
    )

    db.session.add(product)
    db.session.commit()

    flash("Product added successfully.", "success")
    return redirect(url_for("admin.products"))

@admin.route("/products/edit/<int:product_id>", methods=["POST"])
@admin_login_required
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)

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

@admin.route("/products/delete/<int:product_id>", methods=["POST"])
@admin_login_required
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)

    db.session.delete(product)
    db.session.commit()

    flash("Product deleted successfully.", "success")
    return redirect(url_for("admin.products"))

@admin.route("/orders")
@admin_login_required
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
@admin_login_required
def customers():
    orders = Order.query.order_by(Order.id.desc()).all()

    customers = {}

    for order in orders:
        key = order.customer_phone

        if key not in customers:
            customers[key] = {
                "id": len(customers) + 1,
                "name": order.customer_name,
                "phone": order.customer_phone,
                "email": "N/A",
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
@admin_login_required
def settings():
    setting = SiteSetting.query.first()

    if not setting:
        setting = SiteSetting()
        setting.admin_username = "admin"
        setting.admin_password_hash = generate_password_hash("admin123")

        db.session.add(setting)
        db.session.commit()

    if not setting.admin_password_hash:
        setting.admin_password_hash = generate_password_hash("admin123")
        db.session.commit()

    if request.method == "POST":
        setting.restaurant_name = request.form.get("restaurant_name", "").strip()
        setting.support_email = request.form.get("support_email", "").strip()
        setting.phone = request.form.get("phone", "").strip()
        setting.hours = request.form.get("hours", "").strip()
        setting.address = request.form.get("address", "").strip()

        setting.accept_orders = request.form.get("accept_orders") == "on"
        setting.enable_delivery = request.form.get("enable_delivery") == "on"
        setting.enable_pickup = request.form.get("enable_pickup") == "on"

        setting.admin_name = request.form.get("admin_name", "").strip()
        setting.admin_email = request.form.get("admin_email", "").strip()
        setting.admin_username = request.form.get("admin_username", "").strip()

        new_password = request.form.get("admin_password", "").strip()

        if new_password:
            if len(new_password) < 6:
                flash("Admin password must be at least 6 characters.", "danger")
                return redirect(url_for("admin.settings"))

            setting.admin_password_hash = generate_password_hash(new_password)

        db.session.commit()

        flash("Settings updated successfully.", "success")
        return redirect(url_for("admin.settings"))

    return render_template("admin/settings.html", setting=setting)
    
    