# Used to initialize the Flask application and load the configuration settings from config.py.

from flask import Flask, render_template, redirect, url_for
from flask_login import current_user, login_required
from .config import Config
from .extensions import db, login_manager

from app.routes.auth_route import auth
from app.routes.admin_route import admin
from app.routes.staff_route import staff
from app.routes.user_route import user

from app.seed import create_admin


def create_app():
    app = Flask(__name__)

    # Load configuration from config.py
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message_category = "danger"

    @login_manager.user_loader
    def load_user(user_id):
        from app.models.user_model import User

        if user_id is None:
            return None

        return User.query.get(int(user_id))

    @app.context_processor
    def inject_current_user():
        return dict(current_user=current_user)

    @app.before_request
    def close_booking_deadlines():
        from app.models import Trek

        if Trek.close_due_bookings():
            db.session.commit()

    @app.route("/", endpoint="main.home")
    def home():
        return render_template("index.html")

    @app.route('/dashboard')
    @login_required
    def dashboard():
        if current_user.role == 'ADMIN':
            return redirect(url_for('admin.dashboard'))
        elif current_user.role == 'USER':
            return redirect(url_for('user.dashboard'))

        return redirect(url_for('staff.dashboard'))
    
    from app import models
    
    app.register_blueprint(auth)  
    app.register_blueprint(admin)     
    app.register_blueprint(staff)
    app.register_blueprint(user)

    with app.app_context():
        db.create_all()
        create_admin()

    return app
