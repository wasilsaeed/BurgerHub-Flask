from flask import Blueprint, render_template

main = Blueprint("main", __name__)


products = [
    {
        "id": 1,
        "name": "Classic Beef Burger",
        "category": "Burgers",
        "price": 799,
        "image": "burger.jpg",
        "description": "Juicy grilled beef patty with cheddar cheese, lettuce, tomato, onions, and signature sauce.",
        "is_featured": True,
    },
    {
        "id": 2,
        "name": "Crispy Chicken Burger",
        "category": "Burgers",
        "price": 699,
        "image": "chicken-burger.jpg",
        "description": "Crispy golden chicken fillet with mayo, lettuce, and soft toasted buns.",
        "is_featured": True,
    },
    {
        "id": 3,
        "name": "Loaded Fries",
        "category": "Sides",
        "price": 499,
        "image": "fries.jpg",
        "description": "Crispy fries topped with cheese sauce, jalapeños, and special seasoning.",
        "is_featured": False,
    },
    {
        "id": 4,
        "name": "Chocolate Shake",
        "category": "Drinks",
        "price": 399,
        "image": "shake.jpg",
        "description": "Thick creamy chocolate shake served chilled.",
        "is_featured": False,
    },
]


@main.route("/")
def home():
    featured_products = [product for product in products if product["is_featured"]]
    return render_template('index.html', featured_products=featured_products)

@main.route("/menu")
def menu():
    return render_template("menu.html", products=products)

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

@main.route("/product/<int:product_id>")
def product_detail(product_id):
    product = next((item for item in products if item["id"] == product_id), None)
    return render_template("product_detail.html", product=product)


