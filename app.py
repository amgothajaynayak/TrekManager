import os
from flask import Flask
from flask_login import LoginManager
from config import Config
from models import db, User
from routes import register_blueprints

app = Flask(__name__)
app.config.from_object(Config)

# Initialize db
db.init_app(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Register Blueprints
register_blueprints(app)

@app.errorhandler(404)
def not_found_error(error):
    return "404 Not Found", 404

@app.errorhandler(403)
def forbidden_error(error):
    return "403 Forbidden", 403

def setup_database():
    with app.app_context():
        if not os.path.exists(app.instance_path):
            os.makedirs(app.instance_path)
        db.create_all()
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@trekmanager.com',
                full_name='System Administrator',
                role='admin',
                status='active'
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()

setup_database()

if __name__ == '__main__':
    app.run(debug=True)
