from . import db

class StaffProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)
    specialization = db.Column(db.String(200), nullable=True)
    experience = db.Column(db.String(200), nullable=True)
    bio = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), nullable=False, default='pending')

    user = db.relationship('User', back_populates='staff_profile')

    def __repr__(self):
        return f"<StaffProfile User:{self.user_id}>"
