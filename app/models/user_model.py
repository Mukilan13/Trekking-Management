from datetime import datetime, timezone
from flask_login import UserMixin
from werkzeug.security import check_password_hash

from app.extensions import db


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    
    name = db.Column(db.String(100), nullable=False)
    
    email = db.Column(db.String(120), unique=True, nullable=False)
    
    password = db.Column(db.String(255), nullable=False)
    
    phone = db.Column(db.String(15), nullable=False)

    role = db.Column(
        db.String(20),
        nullable=False,
        default="USER")

    is_approved = db.Column(
        db.Boolean,
        default=False
    )

    is_blacklisted = db.Column(
        db.Boolean,
        default=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.now(timezone.utc)
    )

    def __repr__(self):
        return f"<User {self.name}>"

    def check_password(self, password):
        return check_password_hash(self.password, password)
