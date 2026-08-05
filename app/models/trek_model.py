from datetime import date, datetime

from sqlalchemy.orm import validates

from app.extensions import db


class Trek(db.Model):
    """
    Trek Model

    Relationships:
        - One Staff can manage many Treks.
        - One Trek can have many Bookings.

    Status:
        - Open
        - Closed
        - Started
        - Completed
    """

    __tablename__ = "treks"

    # ------------------------------------------------------------------
    # Constants
    # ------------------------------------------------------------------

    STATUS_OPEN = "Open"
    STATUS_CLOSED = "Closed"
    STATUS_STARTED = "Started"
    STATUS_COMPLETED = "Completed"

    DIFFICULTY_EASY = "Easy"
    DIFFICULTY_MODERATE = "Moderate"
    DIFFICULTY_DIFFICULT = "Difficult"

    # ------------------------------------------------------------------
    # Columns
    # ------------------------------------------------------------------

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(
        db.String(150),
        nullable=False
    )

    location = db.Column(
        db.String(150),
        nullable=False
    )

    difficulty = db.Column(
        db.String(20),
        nullable=False,
        default=DIFFICULTY_MODERATE
    )

    description = db.Column(
        db.Text,
        nullable=True
    )

    start_date = db.Column(
        db.Date,
        nullable=False
    )

    end_date = db.Column(
        db.Date,
        nullable=False
    )

    total_slots = db.Column(
        db.Integer,
        nullable=False,
        default=10
    )

    available_slots = db.Column(
        db.Integer,
        nullable=False,
        default=10
    )

    status = db.Column(
        db.String(20),
        nullable=False,
        default=STATUS_OPEN
    )

    staff_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=True
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------

    staff = db.relationship(
        "User",
        back_populates="treks",
        foreign_keys=[staff_id]
    )

    # ------------------------------------------------------------------
    # Validations
    # ------------------------------------------------------------------

    @validates("difficulty")
    def validate_difficulty(self, key, value):
        allowed = {
            self.DIFFICULTY_EASY,
            self.DIFFICULTY_MODERATE,
            self.DIFFICULTY_DIFFICULT,
        }

        if value not in allowed:
            raise ValueError("Invalid difficulty level.")

        return value

    @validates("status")
    def validate_status(self, key, value):
        allowed = {
            self.STATUS_OPEN,
            self.STATUS_CLOSED,
            self.STATUS_STARTED,
            self.STATUS_COMPLETED,
        }

        if value not in allowed:
            raise ValueError("Invalid trek status.")

        return value

    # ------------------------------------------------------------------
    # Helper Methods
    # ------------------------------------------------------------------

    def is_bookable(self):
        """
        Returns True if booking is allowed.
        """
        return (
            self.status == self.STATUS_OPEN
            and self.available_slots > 0
        )

    def has_started(self):
        """
        Returns True if today's date is
        greater than or equal to start date.
        """
        return self.start_date <= date.today()

    def has_completed(self):
        """
        Returns True if today's date is
        after the trek end date.
        """
        return self.end_date < date.today()

    def auto_close_if_full(self):
        """
        Automatically closes booking when
        available slots become zero.
        """
        if (
            self.available_slots <= 0
            and self.status == self.STATUS_OPEN
        ):
            self.status = self.STATUS_CLOSED

    def book_slot(self):
        """
        Books one slot if available.

        Returns:
            True  -> Booking successful
            False -> Trek not bookable
        """

        if not self.is_bookable():
            return False

        self.available_slots -= 1
        self.auto_close_if_full()

        return True

    def cancel_slot(self):
        """
        Restores one slot after cancellation.
        """

        if self.available_slots < self.total_slots:
            self.available_slots += 1

        if (
            self.status == self.STATUS_CLOSED
            and self.available_slots > 0
        ):
            self.status = self.STATUS_OPEN

    # ------------------------------------------------------------------
    # Representation
    # ------------------------------------------------------------------

    def __repr__(self):
        return (
            f"<Trek "
            f"id={self.id}, "
            f"name='{self.name}', "
            f"status='{self.status}'>"
        )