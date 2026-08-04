from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User, StaffProfile
import re

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()

        if not user or not user.check_password(password):
            flash('Invalid username or password.', 'error')
            return redirect(url_for('auth.login'))

        if user.status == 'blacklisted':
            flash('Your account has been blacklisted. Contact admin.', 'error')
            return redirect(url_for('auth.login'))

        if user.role == 'staff':
            staff_profile = StaffProfile.query.filter_by(user_id=user.id).first()
            if staff_profile:
                if staff_profile.status == 'blacklisted':
                    flash('Your account has been blacklisted. Contact admin.', 'error')
                    return redirect(url_for('auth.login'))
                if staff_profile.status == 'pending':
                    flash('Your account is pending admin approval.', 'warning')
                    return redirect(url_for('auth.login'))

        login_user(user)

        if user.role == 'admin':
            return redirect(url_for('admin.dashboard'))
        elif user.role == 'staff':
            return redirect(url_for('staff.dashboard'))
        else:
            return redirect(url_for('user.dashboard'))

    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        full_name = request.form.get('full_name')
        phone = request.form.get('phone')
        role = request.form.get('role')

        # Validate required fields
        if not all([username, email, password, confirm_password, full_name, phone, role]):
            flash('All base fields are required.', 'error')
            return redirect(url_for('auth.register'))
            
        if role not in ['trekker', 'staff']:
            flash('Invalid role selected.', 'error')
            return redirect(url_for('auth.register'))

        if len(password) < 6:
            flash('Password minimum 6 characters.', 'error')
            return redirect(url_for('auth.register'))

        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return redirect(url_for('auth.register'))

        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            flash('Invalid email format.', 'error')
            return redirect(url_for('auth.register'))

        if User.query.filter_by(username=username).first():
            flash('Username is already taken.', 'error')
            return redirect(url_for('auth.register'))

        if User.query.filter_by(email=email).first():
            flash('Email is already registered.', 'error')
            return redirect(url_for('auth.register'))

        # Check staff-specific fields if applicable
        specialization = request.form.get('specialization')
        experience = request.form.get('experience')
        bio = request.form.get('bio')

        if role == 'staff':
            if not all([specialization, experience, bio]):
                flash('All staff fields are required.', 'error')
                return redirect(url_for('auth.register'))

        # Create User
        user = User(
            username=username,
            email=email,
            full_name=full_name,
            phone=phone,
            role=role,
            status='active'
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        # Create StaffProfile if role is staff
        if role == 'staff':
            staff_profile = StaffProfile(
                user_id=user.id,
                specialization=specialization,
                experience=experience,
                bio=bio,
                status='pending'
            )
            db.session.add(staff_profile)
            db.session.commit()

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('auth.login'))
