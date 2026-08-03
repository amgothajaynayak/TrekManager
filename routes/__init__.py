def register_blueprints(app):
    try:
        from .auth import auth_bp
        from .admin import admin_bp
        from .staff import staff_bp
        from .user import user_bp

        app.register_blueprint(auth_bp)
        app.register_blueprint(admin_bp, url_prefix='/admin')
        app.register_blueprint(staff_bp, url_prefix='/staff')
        app.register_blueprint(user_bp, url_prefix='/user')
    except ImportError:
        pass
