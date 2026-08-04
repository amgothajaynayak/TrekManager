from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required
from datetime import datetime
from models import db, User, Trek, Booking, StaffProfile
from utils.decorators import admin_required

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    total_treks = Trek.query.count()
    total_users = User.query.filter_by(role='trekker').count()
    total_staff = User.query.filter_by(role='staff').count()
    total_bookings = Booking.query.count()
    pending_staff = StaffProfile.query.filter_by(status='pending').count()
    open_treks = Trek.query.filter_by(status='Open').count()
    recent_bookings = Booking.query.order_by(Booking.booking_date.desc()).limit(5).all()

    return render_template('admin/dashboard.html',
                           total_treks=total_treks,
                           total_users=total_users,
                           total_staff=total_staff,
                           total_bookings=total_bookings,
                           pending_staff=pending_staff,
                           open_treks=open_treks,
                           recent_bookings=recent_bookings)


@admin_bp.route('/treks')
@login_required
@admin_required
def manage_treks():
    treks = Trek.query.order_by(Trek.created_at.desc()).all()
    return render_template('admin/manage_treks.html', treks=treks)


@admin_bp.route('/treks/new', methods=['GET', 'POST'])
@login_required
@admin_required
def create_trek():
    if request.method == 'POST':
        name = request.form.get('name')
        location = request.form.get('location')
        difficulty = request.form.get('difficulty')
        duration_days = request.form.get('duration_days')
        total_slots = request.form.get('total_slots')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        description = request.form.get('description')
        price = request.form.get('price', 0)
        assigned_staff_id = request.form.get('assigned_staff_id')
        status = request.form.get('status', 'Pending')

        if not all([name, location, difficulty, duration_days, total_slots, start_date, end_date]):
            flash('Please fill all required fields.', 'error')
            return redirect(url_for('admin.create_trek'))

        if assigned_staff_id == '' or assigned_staff_id is None:
            assigned_staff_id = None
        else:
            assigned_staff_id = int(assigned_staff_id)

        trek = Trek(
            name=name,
            location=location,
            difficulty=difficulty,
            duration_days=int(duration_days),
            total_slots=int(total_slots),
            available_slots=int(total_slots),
            start_date=datetime.strptime(start_date, '%Y-%m-%d').date(),
            end_date=datetime.strptime(end_date, '%Y-%m-%d').date(),
            description=description,
            price=float(price) if price else 0.0,
            assigned_staff_id=assigned_staff_id,
            status=status
        )
        db.session.add(trek)
        db.session.commit()
        flash('Trek created successfully!', 'success')
        return redirect(url_for('admin.manage_treks'))

    staff_list = User.query.filter_by(role='staff').join(StaffProfile).filter(StaffProfile.status == 'approved').all()
    return render_template('admin/trek_form.html', mode='create', staff_list=staff_list)


@admin_bp.route('/treks/<int:trek_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_trek(trek_id):
    trek = Trek.query.get_or_404(trek_id)

    if request.method == 'POST':
        trek.name = request.form.get('name')
        trek.location = request.form.get('location')
        trek.difficulty = request.form.get('difficulty')
        trek.duration_days = int(request.form.get('duration_days'))

        old_total = trek.total_slots
        new_total = int(request.form.get('total_slots'))
        booked_count = Booking.query.filter_by(trek_id=trek.id, status='Booked').count()
        trek.total_slots = new_total
        trek.available_slots = new_total - booked_count

        trek.start_date = datetime.strptime(request.form.get('start_date'), '%Y-%m-%d').date()
        trek.end_date = datetime.strptime(request.form.get('end_date'), '%Y-%m-%d').date()
        trek.description = request.form.get('description')
        price = request.form.get('price', 0)
        trek.price = float(price) if price else 0.0
        trek.status = request.form.get('status', trek.status)

        assigned_staff_id = request.form.get('assigned_staff_id')
        if assigned_staff_id == '' or assigned_staff_id is None:
            trek.assigned_staff_id = None
        else:
            trek.assigned_staff_id = int(assigned_staff_id)

        db.session.commit()
        flash('Trek updated successfully!', 'success')
        return redirect(url_for('admin.manage_treks'))

    staff_list = User.query.filter_by(role='staff').join(StaffProfile).filter(StaffProfile.status == 'approved').all()
    return render_template('admin/trek_form.html', mode='edit', trek=trek, staff_list=staff_list)


@admin_bp.route('/treks/<int:trek_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_trek(trek_id):
    trek = Trek.query.get_or_404(trek_id)
    Booking.query.filter_by(trek_id=trek.id).delete()
    db.session.delete(trek)
    db.session.commit()
    flash('Trek deleted successfully!', 'success')
    return redirect(url_for('admin.manage_treks'))


@admin_bp.route('/staff')
@login_required
@admin_required
def manage_staff():
    staff_list = User.query.filter_by(role='staff').all()
    return render_template('admin/manage_staff.html', staff_list=staff_list)


@admin_bp.route('/staff/<int:user_id>/approve', methods=['POST'])
@login_required
@admin_required
def approve_staff(user_id):
    user = User.query.get_or_404(user_id)
    if user.staff_profile:
        user.staff_profile.status = 'approved'
        db.session.commit()
        flash(f'Staff {user.full_name} approved!', 'success')
    return redirect(url_for('admin.manage_staff'))


@admin_bp.route('/staff/<int:user_id>/blacklist', methods=['POST'])
@login_required
@admin_required
def blacklist_staff(user_id):
    user = User.query.get_or_404(user_id)
    user.status = 'blacklisted'
    if user.staff_profile:
        user.staff_profile.status = 'blacklisted'
    db.session.commit()
    flash(f'Staff {user.full_name} has been blacklisted.', 'warning')
    return redirect(url_for('admin.manage_staff'))


@admin_bp.route('/staff/<int:user_id>/activate', methods=['POST'])
@login_required
@admin_required
def activate_staff(user_id):
    user = User.query.get_or_404(user_id)
    user.status = 'active'
    if user.staff_profile:
        user.staff_profile.status = 'approved'
    db.session.commit()
    flash(f'Staff {user.full_name} has been activated.', 'success')
    return redirect(url_for('admin.manage_staff'))


@admin_bp.route('/users')
@login_required
@admin_required
def manage_users():
    users = User.query.filter_by(role='trekker').all()
    return render_template('admin/manage_users.html', users=users)


@admin_bp.route('/users/<int:user_id>/blacklist', methods=['POST'])
@login_required
@admin_required
def blacklist_user(user_id):
    user = User.query.get_or_404(user_id)
    user.status = 'blacklisted'
    db.session.commit()
    flash(f'User {user.full_name} has been blacklisted.', 'warning')
    return redirect(url_for('admin.manage_users'))


@admin_bp.route('/users/<int:user_id>/activate', methods=['POST'])
@login_required
@admin_required
def activate_user(user_id):
    user = User.query.get_or_404(user_id)
    user.status = 'active'
    db.session.commit()
    flash(f'User {user.full_name} has been activated.', 'success')
    return redirect(url_for('admin.manage_users'))


@admin_bp.route('/assign-staff', methods=['GET', 'POST'])
@login_required
@admin_required
def assign_staff():
    if request.method == 'POST':
        trek_id = request.form.get('trek_id')
        staff_id = request.form.get('staff_id')

        if not trek_id or not staff_id:
            flash('Please select both a trek and a staff member.', 'error')
            return redirect(url_for('admin.assign_staff'))

        trek = Trek.query.get_or_404(int(trek_id))
        trek.assigned_staff_id = int(staff_id)
        db.session.commit()
        flash(f'Staff assigned to {trek.name} successfully!', 'success')
        return redirect(url_for('admin.assign_staff'))

    treks = Trek.query.all()
    staff_list = User.query.filter_by(role='staff').join(StaffProfile).filter(StaffProfile.status == 'approved').all()
    return render_template('admin/assign_staff.html', treks=treks, staff_list=staff_list)


@admin_bp.route('/bookings')
@login_required
@admin_required
def all_bookings():
    bookings = Booking.query.order_by(Booking.booking_date.desc()).all()
    return render_template('admin/all_bookings.html', bookings=bookings)


@admin_bp.route('/search')
@login_required
@admin_required
def search():
    query = request.args.get('q', '')
    treks = []
    staff = []
    users = []

    if query:
        search_term = f'%{query}%'

        treks = Trek.query.filter(
            db.or_(
                Trek.name.ilike(search_term),
                Trek.location.ilike(search_term),
                Trek.id == int(query) if query.isdigit() else False
            )
        ).all()

        staff = User.query.filter(
            User.role == 'staff'
        ).filter(
            db.or_(
                User.username.ilike(search_term),
                User.full_name.ilike(search_term),
                User.id == int(query) if query.isdigit() else False
            )
        ).all()

        users = User.query.filter(
            User.role == 'trekker'
        ).filter(
            db.or_(
                User.username.ilike(search_term),
                User.full_name.ilike(search_term),
                User.id == int(query) if query.isdigit() else False
            )
        ).all()

    return render_template('admin/search.html', query=query, treks=treks, staff=staff, users=users)
