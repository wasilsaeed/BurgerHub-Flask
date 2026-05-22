from flask import Blueprint, render_template, request, redirect, url_for, flash

from app import db
from app.models import Product

main = Blueprint("main", __name__)


# products = [
#     {
#         "id": 1,
#         "name": "Classic Beef Burger",
#         "category": "Burgers",
#         "price": 799,
#         "image": "burger.jpg",
#         "description": "Juicy grilled beef patty with cheddar cheese, lettuce, tomato, onions, and signature sauce.",
#         "is_featured": True,
#     },
#     {
#         "id": 2,
#         "name": "Crispy Chicken Burger",
#         "category": "Burgers",
#         "price": 699,
#         "image": "chicken-burger.jpg",
#         "description": "Crispy golden chicken fillet with mayo, lettuce, and soft toasted buns.",
#         "is_featured": True,
#     },
#     {
#         "id": 3,
#         "name": "Loaded Fries",
#         "category": "Sides",
#         "price": 499,
#         "image": "fries.jpg",
#         "description": "Crispy fries topped with cheese sauce, jalapeños, and special seasoning.",
#         "is_featured": False,
#     },
#     {
#         "id": 4,
#         "name": "Chocolate Shake",
#         "category": "Drinks",
#         "price": 399,
#         "image": "shake.jpg",
#         "description": "Thick creamy chocolate shake served chilled.",
#         "is_featured": False,
#     },
# ]


@main.route("/")
def home():
    # featured_products = [product for product in products if product["is_featured"]]
    featured_products = Product.query.filter_by(
        is_available = True,
        is_featured = True
    ).limit(4).all()
    return render_template('index.html', featured_products=featured_products)

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
    # product = next((item for item in products if item["id"] == product_id), None)
    product = Product.query.get_or_404(product_id)
    return render_template("product_detail.html", product=product)

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


@main.route("/about")
def about():
    return render_template("about.html")

@main.route("/contact")
def contact():
    return render_template("contact.html")

@main.route("/cart")
def cart():
    return render_template("cart.html")

@main.route("/checkout")
def checkout():
    return render_template("checkout.html")



