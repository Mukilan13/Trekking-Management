from datetime import datetime

from app import db


class Booking(db.Model):
    """
    Booking Model

    Relationships:
        - One User can have many Bookings.
        - One Trek can have many Bookings.

    Status:
        - Confirmed
        - Cancelled

    Note:
        A user can have only one active (Confirmed)
        booking per trek. Duplicate booking validation
        is handled in the booking service/route.
    """

    __tablename__ = "bookings"

    # ------------------------------------------------------------------
    # Constants
    # ------------------------------------------------------------------

    STATUS_CONFIRMED = "Confirmed"
    STATUS_CANCELLED = "Cancelled"

    # ------------------------------------------------------------------
    # Columns
    # ------------------------------------------------------------------

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
    )

    trek_id = db.Column(
        db.Integer,
        db.ForeignKey("treks.id"),
        nullable=False,
    )

    status = db.Column(
        db.String(20),
        nullable=False,
        default=STATUS_CONFIRMED,
    )

    booked_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
    )

    cancelled_at = db.Column(
        db.DateTime,
        nullable=True,
    )

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------

    user = db.relationship(
        "User",
        back_populates="bookings",
        foreign_keys=[user_id],
    )

    trek = db.relationship(
        "Trek",
        back_populates="bookings",
        foreign_keys=[trek_id],
    )

    # ------------------------------------------------------------------
    # Helper Methods
    # ------------------------------------------------------------------

    def is_confirmed(self):
        """
        Returns True if the booking is confirmed.
        """
        return self.status == self.STATUS_CONFIRMED

    def is_cancelled(self):
        """
        Returns True if the booking is cancelled.
        """
        return self.status == self.STATUS_CANCELLED

    def cancel(self):
        """
        Cancels the booking and records
        the cancellation time.
        """
        self.status = self.STATUS_CANCELLED
        self.cancelled_at = datetime.utcnow()

    # ------------------------------------------------------------------
    # Representation
    # ------------------------------------------------------------------

    def __repr__(self):
        return (
            f"<Booking "
            f"id={self.id}, "
            f"user_id={self.user_id}, "
            f"trek_id={self.trek_id}, "
            f"status='{self.status}'>"
        )