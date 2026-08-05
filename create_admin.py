import getpass
import time

from app import create_app
from app.extensions import db
from app.models.user_model import User
from sqlalchemy.exc import OperationalError
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    email = input("Enter admin email: ").strip()
    if not email:
        raise SystemExit("Email is required.")

    existing = User.query.filter_by(email=email).first()
    if existing:
        print(f"A user with email {email} already exists.")
        raise SystemExit(1)

    name = input("Enter admin name: ").strip() or "Administrator"
    phone = input("Enter admin phone number: ").strip() or "0000000000"
    password = getpass.getpass("Enter admin password: ")
    password_confirm = getpass.getpass("Confirm password: ")

    if password != password_confirm:
        raise SystemExit("Passwords do not match.")

    admin = User(
        name=name,
        email=email,
        phone=phone,
        role="ADMIN",
        password=generate_password_hash(password),
        is_approved=True,
    )

    db.session.add(admin)

    for attempt in range(6):
        try:
            db.session.commit()
            break
        except OperationalError as err:
            if "database is locked" in str(err).lower() and attempt < 5:
                print("Database is locked, retrying in 2 seconds...")
                time.sleep(2)
                continue
            raise

    print(f"Admin user created: {admin.email}")
