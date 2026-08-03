from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .user import User
from .trek import Trek
from .booking import Booking
from .staff_profile import StaffProfile
