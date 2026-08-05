# Used to initialize the Flask application and load the configuration settings from config.py.

from flask import Flask, render_template
from flask_login import current_user, login_required
from .config import Config
from .extensions import db, login_manager

from app.routes.auth_route import auth


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

    @app.route("/", endpoint="main.home")
    def home():
        return render_template("index.html")

    @app.route('/dashboard')
    @login_required
    def dashboard():
        if current_user.role == 'ADMIN':
            return render_template('admin/admin_dashboard.html')
        elif current_user.role == 'USER':
            return render_template('user/user_dashboard.html')

        return render_template('staff/staff_dashboard.html')
    
    from app import models
    
    app.register_blueprint(auth)       

    with app.app_context():
        db.create_all()

    return app
