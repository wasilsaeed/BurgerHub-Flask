from app import db
from datetime import datetime

class Product(db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    category = db.Column(db.String(80), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    image = db.Column(db.String(255), nullable=True)
    description = db.Column(db.Text, nullable=False)
    is_featured = db.Column(db.Boolean, default=False)
    is_available = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"Product {self.name}"
    
class Order(db.Model):
    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True)

    customer_name = db.Column(db.String(120), nullable=False)
    customer_phone = db.Column(db.String(50), nullable=False)
    customer_address = db.Column(db.Text, nullable=False)

    payment_method = db.Column(db.String(50), default="cash_on_delivery")
    total_amount = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(50), default="Pending")

    items = db.relationship(
        "OrderItem",
        backref="order",
        lazy=True,
        cascade="all, delete-orphan"
    )
class OrderItem(db.Model):
    __tablename__ = "order_items"

    id = db.Column(db.Integer, primary_key=True)

    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=True)

    product_name = db.Column(db.String(150), nullable=False)
    product_price = db.Column(db.Integer, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    item_total = db.Column(db.Integer, nullable=False)


class ContactMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(150), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class DiscountCode(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False)
    code = db.Column(db.String(30), unique=True, nullable=False)
    used = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class SiteSetting(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    restaurant_name = db.Column(db.String(100), default="BurgerHub")
    support_email = db.Column(db.String(120), default="support@burgerhub.com")
    phone = db.Column(db.String(50), default="+1 555 123 4567")
    hours = db.Column(db.String(100), default="10:00 AM - 11:00 PM")
    address = db.Column(db.Text, default="123 Burger Street, Food City")

    accept_orders = db.Column(db.Boolean, default=True)
    enable_delivery = db.Column(db.Boolean, default=True)
    enable_pickup = db.Column(db.Boolean, default=True)

    admin_name = db.Column(db.String(100), default="Admin")
    admin_email = db.Column(db.String(120), default="admin@burgerhub.com")

    admin_username = db.Column(db.String(80), default="admin")
    admin_password_hash = db.Column(db.String(255), nullable=True)