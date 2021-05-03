from app.acct import bp
from flask import redirect, url_for, render_template
from flask_login import login_required, current_user
from app.models import Shift, Payable, Event
from app import db
import datetime

def admin_check():
    if current_user.user_type != 1:
        flash("You don't have permission to view this page.")
        return redirect(url_for('main.index'))

@bp.route('/acct/generate/invoice')
@login_required
def generate_invoice():
    current_year = int(datetime.datetime.now().strftime('%Y'))
    current_month = int(datetime.datetime.now().strftime('%m'))
    current_day = int(datetime.datetime.now().strftime('%d'))
    if current_day >= 15:
        shifts = Shift.query.filter(Shift.user_id==current_user.id, Shift.is_cancel==False, Shift.is_waitlist==False, Shift.is_noshow==False, Shift.payable_id==None, Shift.location.shift_start >= datetime.datetime(current_year, current_month, 15), Shift.location.shift_start < datetime.datetime.now()).order_by(Shift.timestamp.desc()).all()
    else:
        shifts = Shift.query.filter(Shift.user_id==current_user.id, Shift.is_cancel==False, Shift.is_waitlist==False, Shift.is_noshow==False, Shift.payable_id==None, Shift.location.shift_start >= datetime.datetime(current_year, current_month, 1), Shift.location.shift_start < datetime.datetime.now()).order_by(Shift.timestamp.desc()).all()
    payable_list = []
    for shift in shifts:
        payable = Payable()
        payable.user_id = current_user.id
        payable.shift_id = shift.id
        payable.is_dispute = False
        payable.timestamp = datetime.datetime.now()
        if shift.special_pay:
            payable.amount = shift.special_pay
            payable.memo = shift.special_explanation
            payable.is_flag = True
        else:
            payable.amount = shift.normal_pay
            payable.is_flag = False
        shift.payable_id = payable.id
        payable_list.append(payable)
    db.session.add_all(payable_list)
    db.session.commit()
    flash("Invoice generated!")
    payables = Payable.query.filter(Payable.user_id==current_user.id, Payable.payout_id==None).all()
    return redirect(url_for('acct.view_invoice', user_id=current_user.id))

@bp.route('/admin/acct/dashboard')
@login_required
def dashboard():
    payables = Payable.query.filter_by(payable_id=None).order_by(Payable.timestamp.asc()).all()
    return render_template('acct/dashboard.html', title='Accounting Dashboard', payables=payables)

@bp.route('/admin/acct/view/invoice/<int:user_id>')
@login_required
def view_invoice(user_id):
    user = User.query.filter_by(id=user_id).first_or_404()
    if current_user.user_type != 1:
        user = current_user
    payables = Payable.query.filter(Payable.user_id==user.id, Payable.payout_id==None).all()
    amount_due = 0.
    for payable in payables:
        amount_due += payable.amount
    return render_template('acct/invoice.html', title="{}'s Invoice".format(user.email), payables=payables, amount_due=amount_due)

@bp.route('/admin/acct/generate/payout/<int:payable_id>')
@login_required
def generate_payout(payable_id):
    admin_check()
    payable = Payable.query.filter_by(id=payable_id).first_or_404()
    payout = Payout()
    payout.user_id = payable.user_id
    payout.payable_id = payable.id
    payout.amount = payable.amount
    payout.timestamp = datetime.datetime.now()
    payable.payout_id = payout.id
    db.session.add(payout)
    db.session.commit()
    flash("Payout created.")
    return redirect(url_for('acct.view_invoice', user_id=payable.user_id))

@bp.route('/admin/acct/generate/dispute/<int:payable_id>')
@login_required
def generate_dispute(payable_id):
    admin_check()
    payable = Payable.query.filter_by(id=payable_id).first_or_404()
    payable.is_dispute = True
    db.session.commit()
    flash("Dispute created.")
    return redirect(url_for('acct.view_invoice', user_id=payable.user_id))

@bp.route('/admin/acct/view/payouts/<int:user_id>')
@login_required
def view_payouts(user_id):
    admin_check()
    user = User.query.filter_by(id=user_id).first_or_404()
    payouts = Payout.query.filter_by(user_id=user.id).order_by(Payout.timestamp.desc()).all()
    return render_template('acct/payouts.html', title="{}'s Payouts".format(user.email), user=user, payouts=payouts)

@bp.route('/admin/acct/view/disputes/<int:user_id>')
@login_required
def view_disputes(user_id):
    admin_check()
    user = User.query.filter_by(id=user_id).first_or_404()
    disputes = Payable.query.filter(Payable.user_id==user.id, Payable.is_dispute==True, Payable.payout_id==None).order_by(Payable.timestamp.desc()).all()
    return render_template('acct/disputes.html', title="{}'s Disputes".format(user.email), user=user, disputes=disputes)