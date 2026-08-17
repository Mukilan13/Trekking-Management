from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.extensions import db
from app.models import Booking, Trek
from app.routes.decorators import roles_required


staff = Blueprint("staff", __name__, url_prefix="/staff")


@staff.route("/")
@login_required
@roles_required("STAFF")
def dashboard():
    treks = (
        Trek.query.filter_by(staff_id=current_user.id)
        .order_by(Trek.start_date)
        .all()
    )
    return render_template("staff/staff_dashboard.html", treks=treks)


@staff.route("/treks/<int:trek_id>", methods=["GET", "POST"])
@login_required
@roles_required("STAFF")
def manage_trek(trek_id):
    trek = Trek.query.filter_by(
        id=trek_id,
        staff_id=current_user.id
    ).first_or_404()

    if request.method == "POST":
        action = request.form.get("action")

        if action == "update_slots" and trek.status != Trek.STATUS_COMPLETED and trek.status != Trek.STATUS_STARTED:
            try:
                available_slots = int(request.form.get("available_slots", ""))
            except ValueError:
                available_slots = -1

            active_bookings = trek.bookings.filter_by(
                status=Booking.STATUS_BOOKED
            ).count()
            maximum_available = trek.total_slots - active_bookings

            if not 0 <= available_slots <= maximum_available:
                flash(
                    f"Available slots must be between 0 and {maximum_available}.",
                    "danger",
                )
            else:
                trek.available_slots = available_slots
                trek.auto_close_if_full()
                db.session.commit()
                flash("Available slots updated.", "success")

        elif action == "start" and trek.status == Trek.STATUS_CLOSED:
            if trek.has_started():
                trek.status = Trek.STATUS_STARTED
                db.session.commit()
                flash("Trek started.", "success")
            else:
                flash("This trek can be started on its start date.", "danger")

        elif action == "complete" and trek.status == Trek.STATUS_STARTED:
            if trek.has_completed():
                trek.status = Trek.STATUS_COMPLETED
                for booking in trek.bookings.filter_by(
                    status=Booking.STATUS_BOOKED
                ):
                    booking.status = Booking.STATUS_COMPLETED
                db.session.commit()
                flash("Trek completed.", "success")
            else:
                flash("This trek can be completed only on its end date.", "danger")

        else:
            flash("This action is not available for the trek's current status.", "danger")

        return redirect(
            url_for("staff.manage_trek", trek_id=trek.id)
        )

    participants = (
        trek.bookings.filter_by(status=Booking.STATUS_BOOKED)
        .order_by(Booking.booked_at)
        .all()
    )

    return render_template(
        "staff/manage_trek.html",
        trek=trek,
        participants=participants,
    )
