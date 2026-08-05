from flask import Blueprint, render_template
from flask_login import login_required

from app import db
from app.models.user_model import User
from app.models.trek_model import Trek
from app.forms.trek_form import TrekForm

admin = Blueprint('admin', __name__)

@admin.route('/treks')
@login_required
def manage_treks():
    return render_template(
        'admin/manage_trek.html',
        treks=[],
        q='',
        difficulty='',
        status='',
    )
    
@admin.route('/treks/new', methods=["GET", "POST"])
@login_required
def new_trek():
    form = TrekForm()
    
    approved_staff = User.query.filter_by(role="staff", is_approved=True, is_blacklisted=False).all()


@admin.route("/staff")
@login_required
def manage_staff():
    staff_list = User.query.filter_by(role="staff").order_by(User.created_at.desc()).all()
    return render_template("admin/manage_staff.html", staff_list=staff_list)

@admin.route("/user")
@login_required
def manage_user():
    user_list = User.query.filter_by(role="USER").order_by(User.created_at.desc()).all()
    return render_template("admin/manage_user.html", user_list=user_list)