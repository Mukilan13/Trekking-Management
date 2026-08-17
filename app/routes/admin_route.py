from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required
from sqlalchemy import or_

from app.extensions import db
from app.forms.trek_form import TrekForm
from app.models import Booking, Trek, User
from app.routes.decorators import roles_required


admin = Blueprint("admin", __name__, url_prefix="/admin")


@admin.route("/")
@login_required
@roles_required("ADMIN")
def dashboard():
    return render_template(
        "admin/admin_dashboard.html",
        total_treks=Trek.query.count(),
        open_treks=Trek.query.filter_by(status=Trek.STATUS_OPEN).count(),
        registered_users=User.query.filter_by(role="USER").count(),
        staff_members=User.query.filter_by(role="STAFF").count(),
        pending_staff=User.query.filter_by(
            role="STAFF",
            is_approved=False,
        ).count(),
        total_bookings=Booking.query.count(),
        blacklisted_users=User.query.filter_by(
            is_blacklisted=True,
        ).count(),
        recent_bookings=(
            Booking.query.order_by(Booking.booked_at.desc())
            .limit(8)
            .all()
        ),
    )


@admin.route("/treks")
@login_required
@roles_required("ADMIN")
def manage_treks():
    q = request.args.get("q", "").strip()
    difficulty = request.args.get("difficulty", "")
    status = request.args.get("status", "")

    query = Trek.query

    if q:
        query = query.filter(
            or_(
                Trek.name.ilike(f"%{q}%"),
                Trek.location.ilike(f"%{q}%"),
                Trek.id.cast(db.String).ilike(f"%{q}%"),
            )
        )

    if difficulty:
        query = query.filter_by(difficulty=difficulty)

    if status:
        query = query.filter_by(status=status)

    return render_template(
        "admin/manage_trek.html",
        treks=query.order_by(Trek.start_date).all(),
        q=q,
        difficulty=difficulty,
        status=status,
    )


def _trek_form(trek=None):
    form = TrekForm(obj=trek)

    form.staff_id.choices = [
        (0, "Unassigned")
    ] + [
        (s.id, f"{s.name} (#{s.id})")
        for s in User.query.filter_by(
            role="STAFF",
            is_approved=True,
            is_blacklisted=False,
        ).order_by(User.name)
    ]

    return form


@admin.route("/treks/new", methods=["GET", "POST"])
@login_required
@roles_required("ADMIN")
def new_trek():
    form = _trek_form()

    if form.validate_on_submit():
        trek = Trek(
            name=form.name.data.strip(),
            location=form.location.data.strip(),
            difficulty=form.difficulty.data,
            description=form.description.data.strip(),
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            total_slots=form.total_slots.data,
            available_slots=form.total_slots.data,
            staff_id=form.staff_id.data or None,
        )

        db.session.add(trek)
        db.session.commit()

        flash("Trek created.", "success")
        return redirect(url_for("admin.manage_treks"))

    return render_template(
        "admin/trek_form.html",
        form=form,
        heading="Create Trek",
    )


@admin.route("/treks/<int:trek_id>/edit", methods=["GET", "POST"])
@login_required
@roles_required("ADMIN")
def edit_trek(trek_id):
    trek = db.get_or_404(Trek, trek_id)
    form = _trek_form(trek)

    if form.validate_on_submit():
        booked = trek.total_slots - trek.available_slots

        if form.total_slots.data < booked:
            flash(
                f"Total slots cannot be lower than {booked}, "
                "the current confirmed bookings.",
                "danger",
            )
        else:
            trek.name = form.name.data.strip()
            trek.location = form.location.data.strip()
            trek.difficulty = form.difficulty.data
            trek.description = form.description.data.strip()
            trek.start_date = form.start_date.data
            trek.end_date = form.end_date.data

            trek.available_slots += (
                form.total_slots.data - trek.total_slots
            )
            trek.total_slots = form.total_slots.data
            trek.staff_id = form.staff_id.data or None

            trek.auto_close_if_full()

            db.session.commit()
            flash("Trek updated.", "success")

            return redirect(url_for("admin.manage_treks"))

    return render_template(
        "admin/trek_form.html",
        form=form,
        heading="Edit Trek",
    )


@admin.post("/treks/<int:trek_id>/<action>")
@login_required
@roles_required("ADMIN")
def trek_action(trek_id, action):
    trek = db.get_or_404(Trek, trek_id)

    if action == "delete":
        if trek.bookings.count():
            flash(
                "Treks with booking history cannot be deleted. "
                "Close or complete the trek instead.",
                "warning",
            )
            return redirect(url_for("admin.manage_treks"))

        db.session.delete(trek)
        flash("Trek deleted.", "success")

    elif action == "close":
        trek.status = Trek.STATUS_CLOSED

    elif action == "reopen" and trek.available_slots:
        trek.status = Trek.STATUS_OPEN

    else:
        flash("That action is not available.", "danger")
        return redirect(url_for("admin.manage_treks"))

    db.session.commit()
    flash("Trek status updated.", "success")

    return redirect(url_for("admin.manage_treks"))


@admin.route("/staff")
@login_required
@roles_required("ADMIN")
def manage_staff():
    q = request.args.get("q", "").strip()

    query = User.query.filter_by(role="STAFF")

    if q:
        query = query.filter(
            or_(
                User.name.ilike(f"%{q}%"),
                User.email.ilike(f"%{q}%"),
                User.id.cast(db.String).ilike(f"%{q}%"),
            )
        )

    return render_template(
        "admin/manage_staff.html",
        staff_list=query.order_by(User.created_at.desc()).all(),
        q=q,
    )


@admin.route("/users")
@login_required
@roles_required("ADMIN")
def manage_user():
    q = request.args.get("q", "").strip()

    query = User.query.filter_by(role="USER")

    if q:
        query = query.filter(
            or_(
                User.name.ilike(f"%{q}%"),
                User.email.ilike(f"%{q}%"),
                User.id.cast(db.String).ilike(f"%{q}%"),
            )
        )

    return render_template(
        "admin/manage_user.html",
        users=query.order_by(User.created_at.desc()).all(),
        q=q,
    )


@admin.route("/bookings")
@login_required
@roles_required("ADMIN")
def manage_bookings():
    q = request.args.get("q", "").strip()

    query = Booking.query.join(Booking.user).join(Booking.trek)

    if q:
        query = query.filter(
            or_(
                User.name.ilike(f"%{q}%"),
                Trek.name.ilike(f"%{q}%"),
                Booking.id.cast(db.String).ilike(f"%{q}%"),
            )
        )

    return render_template(
        "admin/manage_bookings.html",
        bookings=query.order_by(Booking.booked_at.desc()).all(),
        q=q,
    )


@admin.post("/staff/<int:staff_id>/<action>")
@login_required
@roles_required("ADMIN")
def staff_action(staff_id, action):
    person = db.get_or_404(User, staff_id)

    if person.role != "STAFF":
        return redirect(url_for("admin.manage_staff"))

    if action == "approve":
        person.is_approved = True

    elif action == "blacklist":
        person.is_blacklisted = True

    elif action == "unblacklist":
        person.is_blacklisted = False

    else:
        flash("Invalid action.", "danger")
        return redirect(url_for("admin.manage_staff"))

    db.session.commit()
    flash("Staff account updated.", "success")

    return redirect(url_for("admin.manage_staff"))


@admin.post("/users/<int:user_id>/<action>")
@login_required
@roles_required("ADMIN")
def user_action(user_id, action):
    person = db.get_or_404(User, user_id)

    if person.role != "USER":
        return redirect(url_for("admin.manage_user"))

    if action == "blacklist":
        person.is_blacklisted = True

    elif action == "unblacklist":
        person.is_blacklisted = False

    else:
        flash("Invalid action.", "danger")
        return redirect(url_for("admin.manage_user"))

    db.session.commit()
    flash("User account updated.", "success")

    return redirect(url_for("admin.manage_user"))