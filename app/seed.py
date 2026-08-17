# app/seed.py
from werkzeug.security import generate_password_hash
from app.extensions import db
from app.models.user_model import User


def create_admin():
    if User.query.filter_by(email="admin@trek.com").first():
        return

    admin = User(
        name="Administrator",
        email="admin@trek.com",
        password=generate_password_hash("Admin@123"),
        phone="9999999999",
        role="ADMIN",
        is_approved=True,
        is_blacklisted=False,
    )

    db.session.add(admin)
    db.session.commit()