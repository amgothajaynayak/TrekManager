from flask import Blueprint, render_template, request, flash, redirect, url_for, abort
from flask_login import login_required, current_user
from models import db, User, Trek, Booking, StaffProfile
from utils.decorators import staff_required

staff = Blueprint('staff', __name__, url_prefix='/staff')

@staff.route('/dashboard')
@login_required
@staff_required
def dashboard():
    assigned_treks = Trek.query.filter_by(assigned_staff_id=current_user.id).all()
    total_participants = sum(t.total_slots - t.available_slots for t in assigned_treks if t.total_slots is not None and t.available_slots is not None)
    
    return render_template('staff/dashboard.html', assigned_treks=assigned_treks, total_participants=total_participants)

@staff.route('/treks')
@login_required
@staff_required
def treks():
    assigned_treks = Trek.query.filter_by(assigned_staff_id=current_user.id).all()
    return render_template('staff/assigned_treks.html', treks=assigned_treks)

@staff.route('/treks/<int:trek_id>')
@login_required
@staff_required
def trek_detail(trek_id):
    trek = Trek.query.get_or_404(trek_id)
    if trek.assigned_staff_id != current_user.id:
        abort(403)
    return render_template('staff/trek_detail.html', trek=trek)

@staff.route('/treks/<int:trek_id>/update', methods=['POST'])
@login_required
@staff_required
def update_trek(trek_id):
    trek = Trek.query.get_or_404(trek_id)
    if trek.assigned_staff_id != current_user.id:
        abort(403)
    
    available_slots_str = request.form.get('available_slots')
    if available_slots_str is not None and available_slots_str.isdigit():
        trek.available_slots = int(available_slots_str)
        
    status = request.form.get('status')
    if status:
        trek.status = status
        
    db.session.commit()
    flash('Trek updated successfully.', 'success')
    return redirect(url_for('staff.trek_detail', trek_id=trek.id))

@staff.route('/treks/<int:trek_id>/participants')
@login_required
@staff_required
def participants(trek_id):
    trek = Trek.query.get_or_404(trek_id)
    if trek.assigned_staff_id != current_user.id:
        abort(403)
    bookings = Booking.query.filter_by(trek_id=trek.id).all()
    return render_template('staff/participants.html', trek=trek, bookings=bookings)

@staff.route('/treks/<int:trek_id>/complete', methods=['POST'])
@login_required
@staff_required
def complete_trek(trek_id):
    trek = Trek.query.get_or_404(trek_id)
    if trek.assigned_staff_id != current_user.id:
        abort(403)
        
    trek.status = 'Completed'
    bookings = Booking.query.filter_by(trek_id=trek.id, status='Booked').all()
    for booking in bookings:
        booking.status = 'Completed'
        
    db.session.commit()
    flash('Trek marked as completed.', 'success')
    return redirect(url_for('staff.trek_detail', trek_id=trek.id))
