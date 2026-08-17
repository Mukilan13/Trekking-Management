from datetime import datetime

from app.extensions import db


class Booking(db.Model):
    __tablename__ = "bookings"

    STATUS_BOOKED = "Booked"
    STATUS_CANCELLED = "Cancelled"
    STATUS_COMPLETED = "Completed"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    trek_id = db.Column(db.Integer, db.ForeignKey("treks.id"), nullable=False)
    status = db.Column(db.String(20), nullable=False, default=STATUS_BOOKED)
    booked_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    cancelled_at = db.Column(db.DateTime)

    user = db.relationship("User", back_populates="bookings", foreign_keys=[user_id])
    trek = db.relationship("Trek", back_populates="bookings", foreign_keys=[trek_id])

    def cancel(self):
        self.status = self.STATUS_CANCELLED
        self.cancelled_at = datetime.utcnow()
