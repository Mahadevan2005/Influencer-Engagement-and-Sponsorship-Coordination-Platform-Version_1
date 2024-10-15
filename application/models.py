from flask_login import UserMixin
from .database import db
from datetime import datetime as dt

class User(UserMixin, db.Model):
    id = db.Column(db.Integer(), primary_key = True)
    username = db.Column(db.String(), nullable = False, unique = True)
    user_role = db.Column(db.Integer(), nullable = False)
    sponsor = db.relationship('Sponsor', backref='user')
    influencer = db.relationship('Influencer', backref='user')

    def get_id(self):
        return str(self.id)

class Admin(UserMixin,db.Model):
    id = db.Column(db.Integer(), primary_key = True)   #0
    username = db.Column(db.String(), nullable = False, unique = True)
    password = db.Column(db.String(), nullable = False)
    admin_id = db.Column(db.Integer(), db.ForeignKey("user.id"), nullable = False)

class Sponsor(db.Model):
    id = db.Column(db.Integer(), primary_key = True)   #1
    company_name = db.Column(db.String(), nullable = False)
    company_budget = db.Column(db.String(), nullable = False)
    username = db.Column(db.String(), nullable = False, unique = True)
    password = db.Column(db.String(), nullable = False)
    industry = db.Column(db.String(), nullable = False)
    flagged = db.Column(db.Integer(), default = 0) 
    campaigns = db.relationship('Campaigns', backref = 'sponsor')
    sponsor_id = db.Column(db.Integer(), db.ForeignKey("user.id"), nullable = False)

class Influencer(db.Model):    #2
    id = db.Column(db.Integer(), primary_key = True)
    name = db.Column(db.String(), nullable = False)
    category = db.Column(db.String(), nullable = False)
    reach = db.Column(db.Integer(), nullable = False)
    niche = db.Column(db.String(), nullable = False)
    platform = db.Column(db.String(), nullable = False)
    username = db.Column(db.String(), nullable = False, unique = True)
    password = db.Column(db.String(), nullable = False)
    flagged = db.Column(db.Integer(), default = 0) 
    adrequests = db.relationship('Adrequests', backref = 'influencer')
    influencer_id = db.Column(db.Integer(), db.ForeignKey("user.id"), nullable = False)

class Campaigns(db.Model):
    id = db.Column(db.Integer(), primary_key = True)
    name = db.Column(db.String(), nullable = False)
    description = db.Column(db.String())
    campaign_budget = db.Column(db.Integer(), nullable = False)
    start_date = db.Column(db.Date(), nullable = False)
    end_date = db.Column(db.Date(), nullable = False)
    visibility = db.Column(db.String(), nullable = False)
    goals = db.Column(db.String(), nullable = False)
    niche = db.Column(db.String(), nullable = False)
    flagged = db.Column(db.Integer(), default = 0)
    sponsor_id = db.Column(db.Integer(), db.ForeignKey("sponsor.id"), nullable = False)
    adrequests = db.relationship('Adrequests', backref = 'campaigns')

class Adrequests(db.Model):
    id = db.Column(db.Integer(), primary_key = True)
    messages = db.Column(db.String())
    requirements = db.Column(db.String(), nullable = False)
    status = db.Column(db.String(), nullable = False)
    payment_amt = db.Column(db.Integer(), nullable = False)
    sent_by_sponsor = db.Column(db.Boolean, default=False)
    campaign_id = db.Column(db.Integer(), db.ForeignKey("campaigns.id"), nullable = False)
    influencer_id = db.Column(db.Integer(), db.ForeignKey("influencer.id"), nullable = True)
