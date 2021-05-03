from app.admin import bp
from app.admin.forms import RegionForm, EventForm, ShiftForm, UserForm
from flask import render_template, redirect, url_for, flash, request, send_from_directory
from app.models import Region, Event, Shift, User
import datetime
from flask_login import login_required, current_user
import json
from app import db

@bp.route('/favicon.ico')
def favicon():
    return send_from_directory('static', 'favicon.ico', mimetype='image/vnd.microsoft.icon')

@bp.route('/admin/dashboard')
@login_required
def dashboard():
    if current_user.user_type != 1:
        flash("You don't have permission to view that page.")
        return redirect(url_for('main.dashboard'))
    regions = Region.query.all()
    if request.args:
        region_id = int(request.args.get('region'))
        region = Region.query.filter_by(id=region_id).first_or_404()
    else:
        region = Region.query.filter_by(id=current_user.region_id).first()
    events = Event.query.filter_by(region_id=region.id).order_by(Event.shift_start.desc()).all()
    event_list = []
    for event in events:
        if event.shift_end < datetime.datetime.now():
            color = '#D3D3D3' #grey
        elif (event.skilled_shift_count() + event.unskilled_shift_count()) / (event.skilled_capacity + event.unskilled_capacity) >= 0.75:
            color = '#00FF00' #green
        elif (event.skilled_shift_count() + event.unskilled_shift_count()) / (event.skilled_capacity + event.unskilled_capacity) >= 0.5:
            color = '#33FFFF' #teal
        elif (event.skilled_shift_count() + event.unskilled_shift_count()) / (event.skilled_capacity + event.unskilled_capacity) >= 0.25:
            color = '#FFFF00' #yellow
        else:
            color = '#FF0000' #red
        data_dict = {
            'title': event.name,
            'start': event.shift_start.strftime("%Y-%m-%dT%H:%M:%S"),
            'end': event.shift_end.strftime("%Y-%m-%dT%H:%M:%S"),
            'url': url_for('admin.view_event', event_id=event.id),
            'color': color
        }
        event_list.append(data_dict)
    return render_template('admin/dashboard.html', title='Dashboard', region=region, event_list=event_list, regions=regions)

# REGIONS

@bp.route('/admin/create/region', methods=['POST', 'GET'])
@login_required
def create_region():
    if current_user.user_type != 1:
        flash("You don't have permission to view that page.")
        return redirect(url_for('main.dashboard'))
    form = RegionForm()
    if form.validate_on_submit():
        region = Region()
        region.name = str(form.name.data)
        db.session.add(region)
        db.session.commit()
        flash("Region created.")
        return redirect(url_for('admin.view_region', region_id=region.id))
    return render_template('admin/region_form.html', title='Create Region', form=form)

@bp.route('/admin/view/region/<int:region_id>')
@login_required
def view_region(region_id):
    if current_user.user_type != 1:
        flash("You don't have permission to view that page.")
        return redirect(url_for('main.dashboard'))
    region = Region.query.filter_by(id=region_id).first_or_404()
    future_events = Event.query.filter(Event.region_id==region.id, Event.shift_start > datetime.datetime.now()).order_by(Event.shift_start.desc()).all()
    events = Event.query.filter_by(region_id=region.id).order_by(Event.shift_start.asc()).all()
    return render_template('admin/region.html', title='View {}'.format(region.name), region=region, events=events)

@bp.route('/admin/edit/region/<int:region_id>', methods=['POST', 'GET'])
@login_required
def edit_region(region_id):
    if current_user.user_type != 1:
        flash("You don't have permission to view that page.")
        return redirect(url_for('main.dashboard'))
    region = Region.query.filter_by(id=region_id).first_or_404()
    form = RegionForm(obj=region)
    if form.validate_on_submit():
        region.name = str(form.name.data)
        db.session.commit()
        flash("Region updated.")
        return redirect(url_for('admin.view_region', region_id=region.id))
    return render_template('admin/region_form.html', title='Edit Region', form=form)

@bp.route('/admin/delete/region/<int:region_id>')
@login_required
def delete_region(region_id):
    if current_user.user_type != 1:
        flash("You don't have permission to view that page.")
        return redirect(url_for('main.dashboard'))
    region = Region.query.filter_by(id=region_id).first_or_404()
    db.session.delete(region)
    db.session.commit()
    flash('Region deleted.')
    return redirect(url_for('admin.dashboard'))

# EVENTS

@bp.route('/admin/create/event', methods=['POST', 'GET'])
@login_required
def create_event():
    if current_user.user_type != 1:
        flash("You don't have permission to view that page.")
        return redirect(url_for('main.dashboard'))
    regions = Region.query.order_by(Region.name.asc()).all()
    region_list = [(i.id, i.name) for i in regions]
    form = EventForm()
    form.region_id.choices = region_list
    if form.validate_on_submit():
        event = Event()
        event.region_id = int(form.region_id.data)
        event.name = str(form.name.data)
        event.shift_start = datetime.datetime.strptime(form.shift_start.data, '%Y-%m-%d %H:%M')
        event.shift_end = datetime.datetime.strptime(form.shift_end.data, '%Y-%m-%d %H:%M')
        event.street_address = str(form.street_address.data)
        event.city = str(form.city.data)
        event.state = str(form.state.data)
        event.zip_code = str(form.zip_code.data)
        event.skilled_capacity = int(form.skilled_capacity.data)
        event.unskilled_capacity = int(form.unskilled_capacity.data)
        event.advance_url = str(form.advance_url.data)
        event.need_drug = bool(form.need_drug.data)
        event.need_background = bool(form.need_background.data)
        event.skilled_base = float(form.skilled_base.data)
        event.unskilled_base = float(form.unskilled_base.data)
        event.special_base = float(form.special_base.data)
        event.special_rate = float(form.special_rate.data)
        event.timestamp = datetime.datetime.now()
        db.session.add(event)
        db.session.commit()
        flash("Event edited.")
        return redirect(url_for('admin.view_event', event_id=event.id))
    return render_template('admin/event_form.html', title='Create Event', form=form)

@bp.route('/admin/view/event/<int:event_id>')
@login_required
def view_event(event_id):
    if current_user.user_type != 1:
        flash("You don't have permission to view that page.")
        return redirect(url_for('main.dashboard'))
    event = Event.query.filter_by(id=event_id).first_or_404()
    region = Region.query.filter_by(id=event.region_id).first()
    return render_template('admin/event.html', title='Event {}'.format(event.name), event=event, region=region)

@bp.route('/admin/edit/event/<int:event_id>', methods=['POST', 'GET'])
@login_required
def edit_event(event_id):
    if current_user.user_type != 1:
        flash("You don't have permission to view that page.")
        return redirect(url_for('main.dashboard'))
    event = Event.query.filter_by(id=event_id).first_or_404()
    regions = Region.query.order_by(Region.name.asc()).all()
    region_list = [(i.id, i.name) for i in regions]
    form = EventForm(obj=event)
    form.region_id.choices = region_list
    if form.validate_on_submit():
        event.region_id = int(form.region_id.data)
        event.name = str(form.name.data)
        event.shift_start = datetime.datetime.strptime(form.shift_start.data, '%Y-%m-%d %H:%M')
        event.shift_end = datetime.datetime.strptime(form.shift_end.data, '%Y-%m-%d %H:%M')
        event.street_address = str(form.street_address.data)
        event.city = str(form.city.data)
        event.state = str(form.state.data)
        event.zip_code = str(form.zip_code.data)
        event.skilled_capacity = int(form.skilled_capacity.data)
        event.unskilled_capacity = int(form.unskilled_capacity.data)
        event.advance_url = str(form.advance_url.data)
        event.need_drug = bool(form.need_drug.data)
        event.need_background = bool(form.need_background.data)
        event.skilled_base = float(form.skilled_base.data)
        event.unskilled_base = float(form.unskilled_base.data)
        event.special_base = float(form.special_base.data)
        event.special_rate = float(form.special_rate.data)
        event.timestamp = datetime.datetime.now()
        db.session.add(event)
        db.session.commit()
        flash("Event edited.")
        return redirect(url_for('admin.view_event', event_id=event.id))
    return render_template('admin/event_form.html', title='Edit Event', form=form)

@bp.route('/admin/delete/event/<int:event_id>')
@login_required
def delete_event(event_id):
    if current_user.user_type != 1:
        flash("You don't have permission to view that page.")
        return redirect(url_for('main.dashboard'))
    event = Event.query.filter_by(id=event_id).first_or_404()
    db.session.delete(event)
    db.session.commit()
    flash("Event deleted.")
    return redirect(url_for('admin.dashboard'))

# SHIFTS

@bp.route('/admin/create/shift', methods=['POST', 'GET'])
@login_required
def create_shift():
    if current_user.user_type != 1:
        flash("You don't have permission to view that page.")
        return redirect(url_for('main.dashboard'))
    users = User.query.order_by(User.email.asc()).all()
    user_list = [(i.id, i.email) for i in users]
    events = Event.query.order_by(Event.shift_start.desc()).all()
    event_list = [(i.id, i.name) for i in events]
    form = ShiftForm()
    form.user_id.choices = user_list
    form.event_id.choices = event_list
    if form.validate_on_submit():
        event = Event.query.filter_by(id=int(form.event_id.data)).first()
        user = User.query.filter_by(id=int(form.user_id.data)).first()
        shift = Shift()
        shift.user_id = int(form.user_id.data)
        shift.event_id = int(form.event_id.data)
        shift.payable_id = None
        if form.special_explanation.data == '' and int(form.special_units.data) == 0:
            if user.user_type == 2:
                shift.normal_pay = float(event.skilled_base)
                shift.special_pay = float(0)
                shift.special_units = int(0)
                shift.special_explanation = None
            elif user.user_type == 3:
                shift.normal_pay = float(event.unskilled_base)
                shift.special_pay = float(0)
                shift.special_units = int(0)
                shift.special_explanation = None
            else:
                shift.normal_pay = float(0)
                shift.special_pay = float(0)
                shift.special_units = int(0)
                shift.explanation = 'Pay rate not defined for this user type.'
        else:
            shift.normal_pay = float(0)
            shift.special_pay = event.special_base + (event.special_rate * int(form.special_units.data))
            shift.special_units = int(form.special_units.data)
            shift.special_explanation = str(form.special_explanation.data)
        shift.shift_start = str(form.shift_start.data)
        shift.lunch_start = str(form.lunch_start.data)
        shift.lunch_end = str(form.lunch_end.data)
        shift.shift_end = str(form.shift_end.data)
        shift.is_cancel = bool(form.is_cancel.data)
        shift.is_waitlist = bool(form.is_waitlist.data)
        shift.is_noshow = bool(form.is_noshow.data)
        shift.timestamp = datetime.datetime.now()
        db.session.add(shift)
        db.session.commit()
        flash("Shift created.")
        return redirect(url_for('admin.view_shift', shift_id=shift.id))
    return render_template('admin/shift_form.html', title='Create Shift', form=form)

@bp.route('/admin/view/shift/<int:shift_id>')
@login_required
def view_shift(shift_id):
    if current_user.user_type != 1:
        flash("You don't have permission to view that page.")
        return redirect(url_for('main.dashboard'))
    shift = Shift.query.filter_by(id=shift_id).first_or_404()
    return render_template('admin/shift.html', title='View Shift', shift=shift)

@bp.route('/admin/edit/shift/<int:shift_id>', methods=['POST', 'GET'])
@login_required
def edit_shift(shift_id):
    if current_user.user_type != 1:
        flash("You don't have permission to view that page.")
        return redirect(url_for('main.dashboard'))
    shift = Shift.query.filter_by(id=shift_id).first_or_404()
    users = User.query.order_by(User.email.asc()).all()
    user_list = [(i.id, i.email) for i in users]
    events = Event.query.order_by(Event.shift_start.desc()).all()
    event_list = [(i.id, i.name) for i in events]
    form = ShiftForm(obj=shift)
    form.user_id.choices = user_list
    form.event_id.choices = event_list
    if form.validate_on_submit():
        event = Event.query.filter_by(id=int(form.event_id.data)).first()
        user = User.query.filter_by(id=int(form.user_id.data)).first()
        shift.user_id = int(form.user_id.data)
        shift.event_id = int(form.event_id.data)
        shift.payable_id = None
        if form.special_explanation.data == '' and int(form.special_units.data) == 0:
            if user.user_type == 2:
                shift.normal_pay = float(event.skilled_base)
                shift.special_pay = float(0)
                shift.special_units = int(0)
                shift.special_explanation = None
            elif user.user_type == 3:
                shift.normal_pay = float(event.unskilled_base)
                shift.special_pay = float(0)
                shift.special_units = int(0)
                shift.special_explanation = None
            else:
                shift.normal_pay = float(0)
                shift.special_pay = float(0)
                shift.special_units = int(0)
                shift.explanation = 'Pay rate not defined for this user type.'
        else:
            shift.normal_pay = float(0)
            shift.special_pay = event.special_base + (event.special_rate * int(form.special_units.data))
            shift.special_units = int(form.special_units.data)
            shift.special_explanation = str(form.special_explanation.data)
        shift.shift_start = str(form.shift_start.data)
        shift.lunch_start = str(form.lunch_start.data)
        shift.lunch_end = str(form.lunch_end.data)
        shift.shift_end = str(form.shift_end.data)
        shift.is_cancel = bool(form.is_cancel.data)
        shift.is_waitlist = bool(form.is_waitlist.data)
        shift.is_noshow = bool(form.is_noshow.data)
        shift.timestamp = datetime.datetime.now()
        db.session.commit()
        flash("Shift updated.")
        return redirect(url_for('admin.view_shift', shift_id=shift.id))
    return render_template('admin/shift_form.html', title='Edit Shift', form=form)

@bp.route('/admin/delete/shift/<int:shift_id>')
@login_required
def delete_shift(shift_id):
    if current_user.user_type != 1:
        flash("You don't have permission to view that page.")
        return redirect(url_for('main.dashboard'))
    shift = Shift.query.filter_by(id=shift_id).first_or_404()
    db.session.delete(shift)
    db.session.commit()
    flash("Shift deleted.")
    return redirect(url_for('admin.dashboard'))

# USERS

@bp.route('/admin/create/user', methods=['POST', 'GET'])
@login_required
def create_user():
    if current_user.user_type != 1:
        flash("You don't have permission to view that page.")
        return redirect(url_for('main.dashboard'))
    regions = Region.query.order_by(Region.name.asc()).all()
    region_list = [(i.id, i.name) for i in regions]
    form = UserForm()
    form.region_id.choices = region_list
    if form.validate_on_submit():
        user = User()
        user.region_id = int(form.region_id.data)
        user.stripe_customer_id = str(form.stripe_customer_id.data)
        user.email = str(form.email.data)
        user.password_hash = user.set_password(str(form.password.data))
        user.first_name = str(form.first_name.data)
        user.last_name = str(form.last_name.data)
        user.user_type = int(form.user_type.data)
        user.comments = str(form.comments.data)
        user.is_blacklist = bool(form.is_blacklist.data)
        user.is_drug = bool(form.is_drug.data)
        user.is_background = bool(form.is_background.data)
        user.last_active = datetime.datetime.now()
        db.session.add(user)
        db.session.commit()
        flash("User created.")
        return redirect(url_for('admin.view_user', user_id=user.id))
    return render_template('admin/user_form.html', title='Create User', form=form)

@bp.route('/admin/view/user/<int:user_id>')
@login_required
def view_user(user_id):
    if current_user.user_type != 1:
        flash("You don't have permission to view that page.")
        return redirect(url_for('main.dashboard'))
    user = User.query.filter_by(id=user_id).first_or_404()
    region = Region.query.filter_by(id=user.region_id).first()
    past_shifts = Shift.query.filter(Shift.user_id==user.id, Shift.shift_start < datetime.datetime.now()).all()
    future_shifts = Shift.query.filter(Shift.user_id==user.id, Shift.shift_start > datetime.datetime.now()).all()
    return render_template('admin/user.html', title='User {}'.format(user.email), user=user, region=region, past_shifts=past_shifts, future_shifts=future_shifts)

@bp.route('/admin/edit/user/<int:user_id>', methods=['POST', 'GET'])
@login_required
def edit_user(user_id):
    if current_user.user_type != 1:
        flash("You don't have permission to view that page.")
        return redirect(url_for('main.dashboard'))
    user = User.query.filter_by(id=user_id).first_or_404()
    regions = Region.query.order_by(Region.name.asc()).all()
    region_list = [(i.id, i.name) for i in regions]
    form = UserForm(obj=user)
    form.region_id.choices = region_list
    if form.validate_on_submit():
        user.region_id = int(form.region_id.data)
        user.stripe_customer_id = str(form.stripe_customer_id.data)
        user.email = str(form.email.data)
        user.set_password(str(form.password.data))
        user.first_name = str(form.first_name.data)
        user.last_name = str(form.last_name.data)
        user.user_type = int(form.user_type.data)
        user.comments = str(form.comments.data)
        user.is_blacklist = bool(form.is_blacklist.data)
        user.is_drug = bool(form.is_drug.data)
        user.is_background = bool(form.is_background.data)
        user.last_active = datetime.datetime.now()
        db.session.commit()
        flash("User updated.")
        return redirect(url_for('admin.view_user', user_id=user.id))
    return render_template('admin/user_form.html', title='Edit User', form=form)

@bp.route('/admin/delete/user/<int:user_id>')
@login_required
def delete_user(user_id):
    if current_user.user_type != 1:
        flash("You don't have permission to view that page.")
        return redirect(url_for('main.dashboard'))
    user = User.query.filter_by(id=user_id).first_or_404()
    db.session.delete(user)
    db.session.commit()
    flash('User deleted.')
    return redirect(url_for('admin.dashboard'))