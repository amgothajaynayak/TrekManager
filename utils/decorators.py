from functools import wraps
from flask import abort, redirect, url_for
from flask_login import current_user

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        if current_user.role != 'admin':
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

def staff_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        if current_user.role != 'staff' or current_user.status != 'active':
            abort(403)
        if not current_user.staff_profile or current_user.staff_profile.status != 'approved':
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

def trekker_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        if current_user.role != 'trekker' or current_user.status != 'active':
            abort(403)
        return f(*args, **kwargs)
    return decorated_function
