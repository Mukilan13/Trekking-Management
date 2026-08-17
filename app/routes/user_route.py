from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy import or_

from app.extensions import db
from app.models import Booking, Trek
from app.routes.decorators import roles_required


user = Blueprint("user", __name__, url_prefix="/user")


@user.route("/")
@login_required
@roles_required("USER")
def dashboard():
    q = request.args.get("q", "").strip()
    difficulty = request.args.get("difficulty", "")
    location = request.args.get("location", "")

    query = Trek.query.filter_by(status=Trek.STATUS_OPEN)

    if q:
        query = query.filter(
            or_(
                Trek.name.ilike(f"%{q}%"),
                Trek.location.ilike(f"%{q}%"),
            )
        )

    if difficulty:
        query = query.filter_by(difficulty=difficulty)

    if location:
        query = query.filter(Trek.location.ilike(f"%{location}%"))

    bookings = (
        Booking.query.filter_by(user_id=current_user.id)
        .order_by(Booking.booked_at.desc())
        .all()
    )

    booked_ids = {
        b.trek_id
        for b in bookings
        if b.status == Booking.STATUS_BOOKED
    }

    return render_template(
        "user/user_dashboard.html",
        treks=query.order_by(Trek.start_date).all(),
        bookings=bookings,
        booked_ids=booked_ids,
        q=q,
        difficulty=difficulty,
        location=location,
    )


@user.post("/treks/<int:trek_id>/book")
@login_required
@roles_required("USER")
def book(trek_id):
    trek = db.get_or_404(Trek, trek_id)

    existing = Booking.query.filter_by(
        user_id=current_user.id,
        trek_id=trek.id,
        status=Booking.STATUS_BOOKED,
    ).first()

    if existing:
        flash("You already have a booking for this trek.", "warning")

    elif not trek.is_bookable():
        flash("This trek is not available for booking.", "danger")

    else:
        trek.book_slot()
        db.session.add(
            Booking(
                user_id=current_user.id,
                trek_id=trek.id,
            )
        )
        db.session.commit()
        flash("Your trek booking is confirmed!", "success")

    return redirect(url_for("user.dashboard"))


@user.post("/bookings/<int:booking_id>/cancel")
@login_required
@roles_required("USER")
def cancel(booking_id):
    booking = Booking.query.filter_by(
        id=booking_id,
        user_id=current_user.id,
    ).first_or_404()

    if booking.status != Booking.STATUS_BOOKED:
        flash("Only active bookings can be cancelled.", "warning")

    elif booking.trek.status == Trek.STATUS_STARTED:
        flash("This booking can no longer be cancelled, as the trek has started.", "danger")

    else:
        booking.cancel()
        booking.trek.cancel_slot()
        db.session.commit()
        flash("Booking cancelled and slot restored.", "success")

    return redirect(url_for("user.dashboard"))


@user.route("/profile", methods=["GET", "POST"])
@login_required
@roles_required("USER")
def profile():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        phone = request.form.get("phone", "").strip()

        if (
            len(name) < 3
            or not phone.isdigit()
            or len(phone) != 10
        ):
            flash(
                "Enter a name and a valid 10-digit phone number.",
                "danger",
            )
        else:
            current_user.name = name
            current_user.phone = phone
            db.session.commit()
            flash("Profile updated.", "success")

    return render_template("user/profile.html")