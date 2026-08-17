from werkzeug.security import generate_password_hash

from app.extensions import db
from app.models.user_model import User

class AuthService:
    
    @staticmethod
    def get_dashboard_template(user):
        return
    
    @staticmethod
    def register_user(form):
        existimng_user = User.query.filter_by(
            email=form.email.data.strip().lower()
        ).first()
            
        if existimng_user:
            return False, "Email already exists.", None
            
        hashed_password = generate_password_hash(form.password.data)
            
        user = User(
            name = form.name.data.strip(),
            email = form.email.data.strip().lower(),
            phone = form.phone.data.strip(),
            role = form.role.data,
            password = hashed_password,
            is_approved = False
            if form.role.data == "STAFF"
            else True
        )
            
        db.session.add(user)
        db.session.commit()
            
        return True, "Registration Successful!", user
    
    @staticmethod
    def login_user(form):
        user = User.query.filter_by(
            email = form.email.data.strip().lower()
        ).first()
        
        if not user:
            return False, "Email does not exist.", None
        
        if not user.is_approved:
            return False, "You account is not approved yet.", None

        if user.is_blacklisted:
            return False, "This account is blacklisted.", None
        
        if not user.check_password(form.password.data):
            return False, "Incorrect password.", None
        
        return True, "Login Successful!", user
    
