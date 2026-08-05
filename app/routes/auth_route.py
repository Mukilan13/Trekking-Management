from flask import Blueprint, render_template, flash, redirect, url_for
from flask_login import login_user, logout_user, login_required

from app.forms.auth_form import LoginForm
from app.forms.auth_form import RegisterForm

from app.services.auth_service import AuthService

auth = Blueprint('auth', __name__)

@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    
    if form.validate_on_submit():
        success, message, user = AuthService.register_user(form)
        flash(message, "success" if success else "danger")
            
        if success:
            if user.is_approved:
                login_user(user)
            return redirect(url_for("dashboard"))
    
    return render_template('auth/register.html', form=form)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    
    if form.validate_on_submit():
        success, message, user = AuthService.login_user(form)
        flash(message, "success" if success else "danger")
        
        if success:
            login_user(user)
            return redirect(url_for('dashboard'))
    
    return render_template('auth/login.html', form=form)


@auth.route('/logout', methods=['GET'])
@login_required
def logout():
    # Log out the current user and redirect home
    logout_user()
    flash("You have been logged out.", "success")
    return redirect(url_for('main.home'))


