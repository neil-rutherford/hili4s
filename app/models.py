from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import login
import jwt
import os
import datetime
from time import time

class User(UserMixin, db.Model):
    '''
    user_type: 1-website_admin, 2-skilled, 3-unskilled, 4-other
    timestamp: local
    '''
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    region_id = db.Column(db.Integer, db.ForeignKey('region.id'))
    stripe_customer_id = db.Column(db.String(300))
    email = db.Column(db.String(254), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    user_type = db.Column(db.Integer)
    comments = db.Column(db.String(300))
    is_blacklist = db.Column(db.Boolean)
    is_drug = db.Column(db.Boolean)
    is_background = db.Column(db.Boolean)
    shifts = db.relationship('Shift', backref='worker', lazy='dynamic')
    payables = db.relationship('Payable', backref='creditor', lazy='dynamic')
    payouts = db.relationship('Payout', backref='payee', lazy='dynamic')
    last_active = db.Column(db.DateTime)

    def __repr__(self):
        return "<User {}>".format(self.email)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Event(db.Model):
    '''
    shift_start: local
    shift_end: local
    skilled_capacity: how many medical people are needed
    unskilled_capacity: how many "admins" are needed
    skilled_base: what is the base per-diem for a skilled worker? (e.g. 500 for a "vaccinator" going to commerce city)
    unskilled_base: what is the base per-diem for an unskilled worker? (e.g. 200 for an "admin" person going to commerce city)
    special_base: what is the base per-diem for someone who meets special criteria? (e.g. 250 for a denver person going to pueblo)
    special_rate: what is the per-unit pay for someone who meets special criteria? (e.g. $0.56 per mile)
    timestamp: local
    '''
    __tablename__ = 'event'

    id = db.Column(db.Integer, primary_key=True)
    region_id = db.Column(db.Integer, db.ForeignKey('region.id'))
    name = db.Column(db.String(100))
    shift_start = db.Column(db.DateTime)
    shift_end = db.Column(db.DateTime)
    street_address = db.Column(db.String(100))
    city = db.Column(db.String(50))
    state = db.Column(db.String(2))
    zip_code = db.Column(db.String(5))
    skilled_capacity = db.Column(db.Integer)
    unskilled_capacity = db.Column(db.Integer)
    advance_url = db.Column(db.String(300))
    need_drug = db.Column(db.Boolean)
    need_background = db.Column(db.Boolean)
    skilled_base = db.Column(db.Float)
    unskilled_base = db.Column(db.Float)
    special_base = db.Column(db.Float)
    special_rate = db.Column(db.Float)
    shifts = db.relationship('Shift', backref='location', lazy='dynamic')
    timestamp = db.Column(db.DateTime)

    def __repr__(self):
        return "<Event {}>".format(self.name)
    
    def unskilled_shift_count(self):
        all_shifts = Shift.query.filter(Shift.event_id==self.id, Shift.is_cancel==False, Shift.is_waitlist==False).all()
        unskilled = []
        for shift in all_shifts:
            if shift.worker.user_type == 3:
                unskilled.append(shift)
        return len(unskilled)

    def skilled_shift_count(self):
        all_shifts = Shift.query.filter(Shift.event_id==self.id, Shift.is_cancel==False, Shift.is_waitlist==False).all()
        skilled = []
        for shift in all_shifts:
            if shift.worker.user_type == 2:
                skilled.append(shift)
        return len(skilled)

    def unskilled_waitlist_count(self):
        all_shifts = Shift.query.filter(Shift.event_id==self.id, Shift.is_cancel==False, Shift.is_waitlist==True).all()
        unskilled = []
        for shift in all_shifts:
            if shift.worker.user_type == 3:
                unskilled.append(shift)
        return len(unskilled)

    def skilled_waitlist_count(self):
        all_shifts = Shift.query.filter(Shift.event_id==self.id, Shift.is_cancel==False, Shift.is_waitlist==True).all()
        skilled = []
        for shift in all_shifts:
            if shift.worker.user_type == 2:
                skilled.append(shift)
        return len(skilled)


class Region(db.Model):
    __tablename__ = 'region'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))

    def __repr__(self):
        return "<Region {}>".format(self.name)


class Shift(db.Model):
    '''
    either normal_pay or special_pay, not both
    special_pay: special_base + (special_rate * special_units)
    special_explanation: explain why you qualify for special pay
    is_cancel: did the worker cancel the shift?
    is_waitlist: is the worker on a waitlist?
    is_noshow: did the worker not show up to a shift (no call no show)?
    timestamp: local
    '''
    __tablename__ = 'shift'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'))
    payable_id = db.Column(db.Integer, db.ForeignKey('payable.id'))
    normal_pay = db.Column(db.Float)
    special_pay = db.Column(db.Float)
    special_units = db.Column(db.Integer)
    special_explanation = db.Column(db.String(300))
    shift_start = db.Column(db.String(5))
    lunch_start = db.Column(db.String(5))
    lunch_end = db.Column(db.String(5))
    shift_end = db.Column(db.String(5))
    is_cancel = db.Column(db.Boolean)
    is_waitlist = db.Column(db.Boolean)
    is_noshow = db.Column(db.Boolean)
    timestamp = db.Column(db.DateTime)

    def __repr__(self):
        return "<Shift {}-{}>".format(self.user_id, self.event_id)


class Payable(db.Model):
    '''
    external_reference_id: how is this referenced in highline's own accounting system?
    '''
    __tablename__ = 'payable'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    shift_id = db.Column(db.Integer, db.ForeignKey('shift.id'))
    payout_id = db.Column(db.Integer, db.ForeignKey('payout.id'))
    external_reference_id = db.Column(db.String(300))
    amount = db.Column(db.Float)
    memo = db.Column(db.String(300))
    is_flag = db.Column(db.Boolean)
    is_dispute = db.Column(db.Boolean)
    timestamp = db.Column(db.DateTime)

    def __repr__(self):
        return "<Payable ${} to {}>".format(self.amount, self.user_id)


class Payout(db.Model):
    '''
    external_reference_id: how is this referenced in highline's own accounting system?
    '''
    __tablename__ = 'payout'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    payable_id = db.Column(db.Integer, db.ForeignKey('payable.id'))
    amount = db.Column(db.Float)
    external_reference_id = db.Column(db.String(300))
    timestamp = db.Column(db.DateTime)

    def __repr__(self):
        return "<Payout {} on {}>".format(self.payable_id, self.timestamp)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))