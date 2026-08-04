def register_blueprints(app):
    from .auth import auth_bp
    from .admin import admin_bp
    from .staff import staff
    from .user import user

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(staff)
    app.register_blueprint(user)
