from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Import models so they are registered with SQLAlchemy
from models.user import User
from models.trek import Trek
from models.booking import Booking
from models.staff_profile import StaffProfile
