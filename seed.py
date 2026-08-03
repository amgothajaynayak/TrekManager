import os
from flask import Flask
from config import Config
from models import db, User

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    return app

def seed_db():
    app = create_app()
    with app.app_context():
        # Create instance dir if not exists
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
            print("Admin user created successfully.")
        else:
            print("Admin user already exists.")

if __name__ == '__main__':
    seed_db()
