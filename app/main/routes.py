from app.main import bp
from flask import redirect, url_for, flash, render_template
from app.models import Event, Shift, Region
from app.main.forms import ShiftForm
from flask_login import current_user, login_required
import json
import datetime
from app import db

@bp.route('/')
def index():
    return render_template('main/index.html')

@bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.user_type == 1:
        return redirect(url_for('admin.dashboard'))
        
    events = Event.query.filter_by(region_id=current_user.region_id).all()
    shifts = Shift.query.filter_by(user_id=current_user.id).all()
    past_shifts = []
    future_shifts = []
    for shift in shifts:
        if shift.location.shift_end < datetime.datetime.now():
            past_shifts.append(shift)
        else:
            future_shifts.append(shift)
        
    
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
            'start': event.shift_start.strftime('%Y-%m-%dT%H:%M:%S'),
            'end': event.shift_end.strftime('%Y-%m-%dT%H:%M:%S'),
            'url': url_for('main.view_event', event_id=event.id),
            'color': color
        }
        event_list.append(data_dict)
    return render_template('main/dashboard.html', title='Dashboard', event_list=event_list, past_count=len(past_shifts), future_count=len(future_shifts))

@bp.route('/view/event/<int:event_id>')
@login_required
def view_event(event_id):
    if current_user.is_blacklist:
        flash("You are on a blacklist and are unable to sign up for new shifts.")
        return redirect(url_for('main.index'))
    event = Event.query.filter_by(id=event_id).first_or_404()
    region = Region.query.filter_by(id=event.region_id).first()
    shift = Shift.query.filter(Shift.user_id==current_user.id, Shift.event_id==event.id).first()
    return render_template('main/event.html', title='Event {}'.format(event.name), event=event, region=region, shift=shift)

@bp.route('/create/shift/<int:event_id>')
@login_required
def create_shift(event_id):
    if current_user.is_blacklist:
        flash("You are on a blacklist and are unable to sign up for new shifts.")
        return redirect(url_for('main.index'))
    event = Event.query.filter_by(id=event_id).first_or_404()
    if event.need_drug and not current_user.is_drug:
        flash("You have not completed the drug screen necessary to work at this event.")
        return redirect(url_for('main.dashboard'))
    if event.need_background and not current_user.is_background:
        flash("You have not passed the background check necessary to work at this event.")
        return redirect(url_for('main.dashboard'))
    shift = Shift()
    shift.user_id = current_user.id
    shift.event_id = event.id
    shift.special_pay = float(0)
    shift.special_units = int(0)
    shift.is_cancel = False
    shift.is_noshow = False
    shift.timestamp = datetime.datetime.now()
    if current_user.user_type == 2:
        shift.normal_pay = float(event.skilled_base)
        if event.skilled_shift_count() >= event.skilled_capacity:
            shift.is_waitlist = True
        else:
            shift.is_waitlist = False
    elif current_user.user_type == 3:
        shift.normal_pay = float(event.unskilled_base)
        if event.unskilled_shift_count() >= event.unskilled_capacity:
            shift.is_waitlist = True
        else:
            shift.is_waitlist = False
    else:
        shift.normal_pay = float(0)
        shift.special_explanation = 'Pay cannot be calculated for this user type.'
        shift.is_waitlist = True
    db.session.add(shift)
    db.session.commit()
    if shift.is_waitlist:
        flash("You have been added to the waitlist for this event.")
    else:
        flash("You have been scheduled for this event.")
    return redirect(url_for('main.view_shift', shift_id=shift.id))
    

@bp.route('/view/shift/<int:shift_id>', methods=["GET", "POST"])
@login_required
def view_shift(shift_id):
    if current_user.is_blacklist:
        flash("You are on a blacklist and are unable to sign up for new shifts.")
        return redirect(url_for('main.index'))
    shift = Shift.query.filter_by(id=shift_id).first_or_404()
    event = Event.query.filter_by(id=shift.event_id).first()
    form = ShiftForm(obj=shift)
    if form.validate_on_submit():
        shift.shift_start = str(form.shift_start.data)
        shift.lunch_start = str(form.lunch_start.data)
        shift.lunch_end = str(form.lunch_end.data)
        shift.shift_end = str(form.shift_end.data)
        shift.timestamp = datetime.datetime.now()
        if form.special_units.data != '' and form.special_explanation.data != '':
            shift.normal_pay = float(0)
            shift.special_units = int(form.special_units.data)
            shift.special_explanation = str(form.special_explanation.data)
            shift.special_pay = float(event.special_base + (event.special_rate * int(form.special_units.data)))
        db.session.commit()
        flash("Shift updated!")
        return redirect(url_for('main.view_shift', shift_id=shift.id))
    return render_template('main/shift.html', title='View Shift', shift=shift, event=event, form=form)

@bp.route('/cancel/shift/<int:shift_id>')
@login_required
def cancel_shift(shift_id):
    if current_user.is_blacklist:
        flash("You are on a blacklist and are unable to sign up for new shifts.")
        return redirect(url_for('main.index'))
    shift = Shift.query.filter_by(id=shift_id).first_or_404()
    if shift.user_id != current_user.id:
        flash("You don't have permission to cancel that shift.")
        return redirect(url_for('main.dashboard'))
    event = Event.query.filter_by(id=shift.event_id).first()
    #if event.shift_start - datetime.datetime.now() < datetime.timedelta(seconds=43200):
        #flash("You must provide 12 hours or more of notice before canceling a shift.")
        #return redirect(url_for('main.dashboard'))
    shift.is_cancel = True
    if current_user.user_type == 2:
        if event.skilled_waitlist_count() > 0 and not shift.is_waitlist:
            waitlist = Shift.query.filter(Shift.event_id==event.id, Shift.is_waitlist==True, Shift.worker.user_type==2).all()
            waitlist[0].is_waitlist = False
    elif current_user.user_type == 3:
        if event.unskilled_waitlist_count() > 0 and not shift.is_waitlist:
            waitlist = Shift.query.filter(Shift.event_id==event.id, Shift.is_waitlist==True, Shift.worker.user_type==3).all()
            waitlist[0].is_waitlist = False
    db.session.commit()
    flash("Shift successfully canceled.")
    return redirect(url_for('main.view_shift', shift_id=shift.id))

@bp.route('/view/shifts/past')
@login_required
def view_past_shifts():
    shifts = Shift.query.filter_by(user_id=current_user.id).all()
    past_shifts = []
    for shift in shifts:
        if shift.location.shift_end < datetime.datetime.now():
            past_shifts.append(shift)
    return render_template('main/shifts.html', title='View Past Shifts', shifts=past_shifts)

@bp.route('/view/shifts/future')
@login_required
def view_future_shifts():
    shifts = Shift.query.filter_by(user_id=current_user.id).all()
    future_shifts = []
    for shift in shifts:
        if shift.location.shift_end > datetime.datetime.now():
            future_shifts.append(shift)
    return render_template('main/shifts.html', title='View Future Shifts', shifts=future_shifts)