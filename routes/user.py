from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db, User, Trek, Booking
from utils.decorators import trekker_required

user = Blueprint('user', __name__, url_prefix='/user')

@user.route('/dashboard')
@login_required
@trekker_required
def dashboard():
    active_bookings = Booking.query.filter_by(user_id=current_user.id, status='Booked').all()
    completed_count = Booking.query.filter_by(user_id=current_user.id, status='Completed').count()
    open_treks_count = Trek.query.filter_by(status='Open').count()
    return render_template('user/dashboard.html', active_bookings=active_bookings, completed_count=completed_count, open_treks_count=open_treks_count)

@user.route('/treks')
@login_required
@trekker_required
def browse_treks():
    difficulty = request.args.get('difficulty', 'All')
    search = request.args.get('search', '')
    query = Trek.query.filter_by(status='Open')
    if difficulty != 'All':
        query = query.filter_by(difficulty=difficulty)
    if search:
        search_term = f"%{search}%"
        query = query.filter((Trek.name.ilike(search_term)) | (Trek.location.ilike(search_term)))
    treks = query.all()
    return render_template('user/browse_treks.html', treks=treks, search=search, difficulty=difficulty)

@user.route('/treks/<int:trek_id>')
@login_required
@trekker_required
def trek_detail(trek_id):
    trek = Trek.query.get_or_404(trek_id)
    existing_booking = Booking.query.filter_by(user_id=current_user.id, trek_id=trek.id, status='Booked').first()
    return render_template('user/trek_detail.html', trek=trek, existing_booking=existing_booking)

@user.route('/treks/<int:trek_id>/book', methods=['POST'])
@login_required
@trekker_required
def book_trek(trek_id):
    trek = Trek.query.get_or_404(trek_id)
    if trek.status != 'Open':
        flash('Trek is not open for booking', 'danger')
        return redirect(url_for('user.trek_detail', trek_id=trek.id))
    if trek.available_slots <= 0:
        flash('Trek is fully booked', 'danger')
        return redirect(url_for('user.trek_detail', trek_id=trek.id))
    existing_booking = Booking.query.filter_by(user_id=current_user.id, trek_id=trek.id, status='Booked').first()
    if existing_booking:
        flash('You already have an active booking for this trek', 'warning')
        return redirect(url_for('user.trek_detail', trek_id=trek.id))
    new_booking = Booking(user_id=current_user.id, trek_id=trek.id, status='Booked')
    trek.available_slots -= 1
    db.session.add(new_booking)
    db.session.commit()
    flash('Successfully booked the trek', 'success')
    return redirect(url_for('user.my_bookings'))

@user.route('/treks/<int:trek_id>/cancel', methods=['POST'])
@login_required
@trekker_required
def cancel_booking(trek_id):
    booking = Booking.query.filter_by(user_id=current_user.id, trek_id=trek_id, status='Booked').first()
    if not booking:
        flash('Booking not found', 'danger')
        return redirect(url_for('user.my_bookings'))
    booking.status = 'Cancelled'
    trek = Trek.query.get(trek_id)
    trek.available_slots += 1
    db.session.commit()
    flash('Booking cancelled successfully', 'success')
    return redirect(url_for('user.my_bookings'))

@user.route('/bookings')
@login_required
@trekker_required
def my_bookings():
    bookings = Booking.query.filter_by(user_id=current_user.id, status='Booked').all()
    return render_template('user/my_bookings.html', bookings=bookings)

@user.route('/history')
@login_required
@trekker_required
def trek_history():
    bookings = Booking.query.filter(Booking.user_id == current_user.id, Booking.status.in_(['Completed', 'Cancelled'])).all()
    return render_template('user/trek_history.html', bookings=bookings)

@user.route('/profile', methods=['GET', 'POST'])
@login_required
@trekker_required
def profile():
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        phone = request.form.get('phone')
        email = request.form.get('email')
        if email != current_user.email:
            existing = User.query.filter_by(email=email).first()
            if existing:
                flash('Email already in use', 'danger')
                return redirect(url_for('user.profile'))
        current_user.full_name = full_name
        current_user.phone = phone
        current_user.email = email
        db.session.commit()
        flash('Profile updated successfully', 'success')
        return redirect(url_for('user.profile'))
    return render_template('user/profile.html')
