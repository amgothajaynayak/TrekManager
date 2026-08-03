from datetime import datetime
from . import db

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    trek_id = db.Column(db.Integer, db.ForeignKey('trek.id'), nullable=False)
    booking_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='Booked')
    notes = db.Column(db.Text, nullable=True)

    user = db.relationship('User', back_populates='bookings')
    trek = db.relationship('Trek', back_populates='bookings')

    __table_args__ = (
        db.UniqueConstraint('user_id', 'trek_id', name='unique_user_trek'),
    )

    def __repr__(self):
        return f"<Booking User:{self.user_id} Trek:{self.trek_id}>"
