from flask import Flask, render_template, redirect, request, url_for, session, flash, abort
from flask_login import login_required, current_user, login_user, logout_user,login_manager
from collections import Counter
from flask import current_app as app
# from sqlalchemy.orm import joinedload
from datetime import datetime,date
from .models import *
import matplotlib  
import matplotlib.ticker as ticker 
import matplotlib.pyplot as plt
matplotlib.use("Agg")

#http://127.0.0.1:5000 base url

#CAMPAIGN ACTIVE/NOT STATUS
def campaign_isactive(start_date,end_date,present_date):
    present_date = date.today()
    return start_date <= present_date < end_date

#PROGRESS CALCULATION 
def calculate_campaign_progress(start_date, end_date):
    current_date = datetime.now().date()
    total_days = (end_date - start_date).days
    elapsed_days = (current_date - start_date).days
    if total_days > 0:
        progress = (elapsed_days / total_days) * 100
    else:
        progress = 0
    return round(progress,2)

# #ACTIVE AD REQEUSTS 
# def get_active_ad_requests(influencer_id):
#     current_date = date.today()
#     active_ad_requests = Adrequests.query.options(joinedload(Adrequests.campaigns)).filter(
#         Adrequests.status == "Accepted by Influencer",Adrequests.influencer_id == influencer_id,
#         Campaigns.start_date <= current_date,Campaigns.end_date > current_date).all()
#     return active_ad_requests


# ------ADMIN-------

#ADMIN LOGIN
@app.route('/adminlogin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        u_name = request.form.get("u_name")
        pwd = request.form.get("pwd")
        this_admin = Admin.query.filter_by(username=u_name).first()
        if not this_admin:
            return render_template('admin_login.html', error="Admin does not exist.")
        if this_admin.password != pwd:
            return render_template('admin_login.html', error="Incorrect password.")
        all_campaigns = Campaigns.query.filter_by(flagged=0).all()
        active_campaigns = [campaign for campaign in all_campaigns if campaign_isactive(campaign.start_date, campaign.end_date, date.today())]
        flagged_influencers = Influencer.query.filter_by(flagged=1).all()
        flagged_sponsors = Sponsor.query.filter_by(flagged=1).all()
        flagged_campaigns = Campaigns.query.filter_by(flagged=1).all()
        login_user(this_admin)
        return render_template('admin_dashboard.html', current_user=u_name, u_name=u_name,
                               active_campaigns=active_campaigns, calculate_campaign_progress=calculate_campaign_progress,
                               flagged_influencers=flagged_influencers, flagged_sponsors=flagged_sponsors,
                               flagged_campaigns=flagged_campaigns)
    return render_template('admin_login.html')


#ADMIN LOGOUT
@app.route('/admin_logout')
@login_required
def admin_logout():
    logout_user()
    return render_template('admin_login.html')


#ADMIN DASHBOARD 
@app.route('/admin_dash', methods=['GET','POST'])
@login_required
def admin_dash():
    id = current_user.id
    admin = Admin.query.get(id)
    u_name = admin.username
    all_campaigns = Campaigns.query.filter_by(flagged=0).all()
    active_campaigns = []
    for campaign in all_campaigns:
            if(campaign_isactive(campaign.start_date,campaign.end_date,date.today())):
                active_campaigns.append(campaign)
    flagged_influencers = Influencer.query.filter_by(flagged=1).all()
    flagged_sponsors = Sponsor.query.filter_by(flagged=1).all()
    flagged_campaigns = Campaigns.query.filter_by(flagged=1).all()
    return render_template('admin_dashboard.html', current_user = u_name, u_name = u_name,
                                        active_campaigns=active_campaigns,
                                        calculate_campaign_progress=calculate_campaign_progress,
                                       flagged_influencers=flagged_influencers, flagged_sponsors=flagged_sponsors,
                                       flagged_campaigns=flagged_campaigns)


#ADMIN FIND PAGE
@app.route('/admin_find',methods=['GET','POST'])
def admin_find():
    campaigns = Campaigns.query.all()
    influencers = Influencer.query.all()
    sponsors = Sponsor.query.all()
    adrequests = Adrequests.query.all()
    return render_template('admin_find.html', campaigns=campaigns, influencers=influencers, sponsors=sponsors,adrequests=adrequests) 


#ADMIN FLAGGING A SPONSOR
@app.route('/flag_sponsor/<int:sponsor_id>', methods=['GET','POST'])
def flag_sponsor(sponsor_id):
    sponsor = Sponsor.query.get(sponsor_id)
    sponsor.flagged = 1
    db.session.commit()
    campaigns = Campaigns.query.filter_by(sponsor_id=sponsor.sponsor_id).all()
    for campaign in campaigns:
        campaign.flagged = 1
    db.session.commit()
    flash('Sponsor has been flagged.', 'success')
    return redirect(url_for('admin_dash')) 


#ADMIN UNFLAGGING A SPONSOR
@app.route('/unflag_sponsor/<int:sponsor_id>', methods=['GET','POST'])
def unflag_sponsor(sponsor_id):
    sponsor = Sponsor.query.get(sponsor_id)
    sponsor.flagged = 0
    db.session.commit()
    campaigns = Campaigns.query.filter_by(sponsor_id=sponsor.sponsor_id).all()
    for campaign in campaigns:
        campaign.flagged = 0
    db.session.commit()
    flash('Sponsor has been Unflagged.', 'success')
    return redirect(url_for('admin_dash')) 


#ADMIN FLAGGING AN INFLUENCER
@app.route('/flag_influencer/<int:influencer_id>', methods=['GET','POST'])
def flag_influencer(influencer_id):
    influencer = Influencer.query.get(influencer_id)
    influencer.flagged = 1
    db.session.commit()
    flash('Influencer has been flagged.', 'success')
    return redirect(url_for('admin_dash'))


#ADMIN UNFLAGGING A INFLUENCER
@app.route('/unflag_influencer/<int:influencer_id>', methods=['GET','POST'])
def unflag_influencer(influencer_id):
    influencer = Influencer.query.get(influencer_id)
    influencer.flagged = 0
    db.session.commit()
    flash('Influencer has been Unflagged.', 'success')
    return redirect(url_for('admin_dash'))


#ADMIN FLAGGING A CAMPAIGN
@app.route('/flag_campaign/<int:campaign_id>', methods=['GET','POST'])
def flag_campaign(campaign_id):
    campaign = Campaigns.query.get(campaign_id)
    campaign.flagged = 1
    db.session.commit()
    flash('Campaign has been flagged.', 'success')
    return redirect(url_for('admin_dash'))


#ADMIN UNFLAGGING A CAMPAIGN
@app.route('/unflag_campaign/<int:campaign_id>', methods=['GET','POST'])
def unflag_campaign(campaign_id):
    campaign = Campaigns.query.get(campaign_id)
    campaign.flagged = 0
    db.session.commit()
    flash('Campaign has been Unflagged.', 'success')
    return redirect(url_for('admin_dash'))



#---------- SPONSOR CAMPAIGN-------

#SPONSOR CREATE CAMPAIGN
@app.route('/create_campaign', methods = ['GET', 'POST'])
@login_required
def create_campaign():
    if request.method == 'POST':
        name = request.form.get("name")
        desc = request.form.get("desc")
        budget = int(request.form.get("budget"))
        if budget <= 0:
            return render_template('create_campaign.html', error="Budget must be greater than 0")
        niche = request.form.get("niche")
        sdate = request.form.get("sdate")
        sdate = datetime.strptime(sdate, '%Y-%m-%d').date()
        edate = request.form.get("edate")
        edate = datetime.strptime(edate, '%Y-%m-%d').date()
        current_date = datetime.now().date()
        if edate < sdate:
            return render_template('create_campaign.html', error="End date cannot be before start date")
        if edate < current_date:
            return render_template('create_campaign.html', error="End date cannot be in the past")
        visibility = request.form.get("visibility").lower()
        goals = request.form.get("goals")
        this_id =  current_user.id
        sponsor = Sponsor.query.filter_by(sponsor_id = this_id).first()
        new_campaign = Campaigns(name = name, description = desc, campaign_budget = budget,niche=niche, start_date = sdate, end_date = edate,
                                 visibility = visibility, goals = goals,sponsor_id = sponsor.sponsor_id)
        db.session.add(new_campaign)
        db.session.commit()
        return redirect('/sponsor_campaign')
    return render_template('create_campaign.html')  


#SPONSOR VIEW REGISTERED INFLUENCERS
@app.route('/registered_influencers')
def registered_influencers():
    influencers = Influencer.query.filter_by(flagged=0).all()
    return render_template('registered_influencers.html', influencers=influencers)


# SPONSOR SENDING ADREQUEST TO INFLUENCER
@app.route('/adrequest/<int:influencer_id>', methods=['GET', 'POST'])
@login_required
def adrequest(influencer_id):
    influencer = Influencer.query.get(influencer_id)
    this_id =  current_user.id
    sponsor = Sponsor.query.filter_by(sponsor_id = this_id).first()
    # cam = sponsor.campaigns
    cam = Campaigns.query.filter_by(sponsor_id=sponsor.sponsor_id).all()
    if request.method == 'POST':
        messages = request.form.get('messages')
        requirements = request.form.get('requirements')
        payment_amt = int(request.form.get('payment_amt'))
        campaign_id = request.form.get('campaign_id')
        campaign = Campaigns.query.get(campaign_id)
        
        if payment_amt >= campaign.campaign_budget:
            return render_template('sponsor_adrequest.html', influencer=influencer, campaigns=cam, error="Payment amount must be less than campaign budget.")

        new_adrequest = Adrequests(
            messages=messages,
            requirements=requirements,
            status = "Requested to Influencer",
            payment_amt=payment_amt,
            campaign_id=campaign_id,
            influencer_id=influencer_id,
            sent_by_sponsor = True
        )

        db.session.add(new_adrequest)
        db.session.commit()
        return redirect(url_for('registered_influencers'))
    return render_template('sponsor_adrequest.html', influencer=influencer, campaigns = cam)



#SPONSOR EDIT AD REQUEST
@app.route('/edit_adrequest/<int:adrequest_id>', methods=['GET', 'POST'])
def edit_adrequest(adrequest_id):
    adrequest = Adrequests.query.get(adrequest_id)
    this_id = current_user.id
    sponsor = Sponsor.query.filter_by(sponsor_id=this_id).first()
    cam = Campaigns.query.filter_by(sponsor_id=sponsor.sponsor_id).all()
    # cam= sponsor.campaigns 
    if request.method == 'POST':
        adrequest.messages = request.form.get('messages')
        adrequest.requirements = request.form.get('requirements')
        # adrequest.status = request.form.get('status')
        adrequest.payment_amt = int(request.form.get('payment_amt'))
        adrequest.campaign_id = request.form.get('campaign_id')
        campaign = Campaigns.query.get(adrequest.campaign_id)
        if adrequest.payment_amt <= 0:
            return render_template('edit_adrequest.html', adrequest=adrequest, campaigns=cam, error="Payment amount must be greater than 0.")
        if adrequest.payment_amt >= campaign.campaign_budget:
            return render_template('edit_adrequest.html', adrequest=adrequest, campaigns=cam, error="Payment amount must be less than campaign budget.")
        db.session.commit() 
        return redirect(url_for('sponsor_campaign'))
    return render_template('edit_adrequest.html', adrequest=adrequest, campaigns=cam)


# SPONSOR DELETE AD REQUEST
@app.route('/delete_adrequest/<int:adrequest_id>', methods=['GET','POST'])
def delete_adrequest(adrequest_id):
    adrequest = Adrequests.query.get(adrequest_id)
    if adrequest:
        db.session.delete(adrequest)
        db.session.commit()
    return redirect(url_for('view_campaign', campaign_id=adrequest.campaign_id))


#SPONSOR VIEW CAMPAIGN
@app.route('/view_campaign/<int:campaign_id>')
def view_campaign(campaign_id):
    campaign = Campaigns.query.get(campaign_id)
    adrequests = db.session.query(Adrequests).join(Influencer).filter(
        Adrequests.campaign_id == campaign_id,
        Adrequests.sent_by_sponsor == True,
        # Influencer.flagged == 0
    ).all()
    # adrequests = Adrequests.query.filter_by(campaign_id=campaign_id ,sent_by_sponsor = True).all()
    progress = calculate_campaign_progress(campaign.start_date, campaign.end_date)
    return render_template('view_campaign.html', campaign=campaign,adrequests=adrequests,progress=progress)      


#SPONSOR DELETE CAMPAIGN
@app.route('/delete_campaign/<int:campaign_id>', methods=['GET','POST'])
def delete_campaign(campaign_id):
    campaign = Campaigns.query.get(campaign_id)
    if campaign:
        db.session.delete(campaign)
        db.session.commit()
    return redirect(url_for('sponsor_campaign'))


#SPONSOR EDIT CAMPAIGN
@app.route('/edit_campaign/<int:campaign_id>', methods=['GET', 'POST'])
def edit_campaign(campaign_id):
    campaign = Campaigns.query.get(campaign_id)
    if request.method == 'POST':
        name = request.form.get("name")
        desc = request.form.get("desc")
        budget = int(request.form.get("budget"))
        if budget <= 0:
            return render_template('edit_campaign.html', campaign=campaign, error="Budget must be greater than 0")
        niche = request.form.get("niche")
        sdate = request.form.get("sdate")
        sdate = datetime.strptime(sdate, '%Y-%m-%d').date()
        edate = request.form.get("edate")
        edate = datetime.strptime(edate, '%Y-%m-%d').date()
        current_date = datetime.now().date()
        if edate < sdate:
            return render_template('edit_campaign.html', campaign=campaign, error="End date cannot be before start date")
        if edate < current_date:
            return render_template('edit_campaign.html', campaign=campaign, error="End date cannot be in the past")
        visibility = request.form.get("visibility").lower()
        goals = request.form.get("goals")
        campaign.name = name
        campaign.description = desc
        campaign.campaign_budget = budget
        campaign.niche = niche
        campaign.start_date = sdate
        campaign.end_date = edate
        campaign.visibility = visibility
        campaign.goals = goals
        db.session.commit()
        return redirect('/sponsor_campaign')
    return render_template('edit_campaign.html', campaign=campaign)


#SPONSOR STATS
@app.route('/sponsor_stats')
@login_required
def sponsor_stats():
    user_id = current_user.id
    user = User.query.get(user_id)
    sponsor = Sponsor.query.filter_by(sponsor_id=user.id).first()
    total_adrequests = Adrequests.query.join(Campaigns).filter(Campaigns.sponsor_id == sponsor.sponsor_id).count()
    accepted_adrequests = Adrequests.query.join(Campaigns).filter(
        Campaigns.sponsor_id == sponsor.sponsor_id,Adrequests.status == 'Accepted by Sponsor').count()
    ongoing_campaigns = Campaigns.query.filter(Campaigns.sponsor_id == sponsor.sponsor_id,Campaigns.flagged == 0).count()
    campaigns = Campaigns.query.filter(Campaigns.sponsor_id == sponsor.sponsor_id,Campaigns.flagged == 0).all()
    completed_campaigns = 0
    for campaign in campaigns:
        if calculate_campaign_progress(campaign.start_date, campaign.end_date) == 100:
            completed_campaigns += 1
    ongoing_campaigns = len(campaigns) - completed_campaigns
    return render_template('sponsor_statistics.html', 
                           total_adrequests=total_adrequests, 
                           accepted_adrequests=accepted_adrequests, 
                           ongoing_campaigns=ongoing_campaigns,
                           completed_campaigns=completed_campaigns)



# -------INFLUENCER-----------

#INFLUENCER LOGOUT
@app.route('/influencer_logout')
@login_required
def influencer_logout():
    logout_user()
    return render_template('influencer_login.html')

#INFLUENCER REGISTER
@app.route('/influencerregister' , methods = ['GET','POST'])
def influencer_reg():
    if request.method == 'POST':
        u_name = request.form.get("u_name")
        pwd = request.form.get("pwd")
        ctg = request.form.get("ctg")
        reach = int(request.form.get("reach"))
        niche = request.form.get("niche")
        platform = request.form.get("platform")
        if not (u_name and pwd and ctg and reach and niche and platform):
            return render_template('influencer_register.html', message="Please fill out all fields and try again.")
        if reach < 0:
            return render_template('influencer_register.html', message="Reach must be greater than 0.")
        this_influencer = Influencer.query.filter_by(username = u_name).first()
        if this_influencer:
            return "influencer already exists"
        else:
            new_user = User(username = u_name, user_role = 2)
            db.session.add(new_user)
            db.session.commit()
            new_influencer = Influencer(name = u_name, category = ctg , reach = reach, niche = niche, platform = platform, username = u_name , password = pwd, influencer_id = new_user.id)
            db.session.add(new_influencer)
            db.session.commit()

            return redirect('/influencerlogin')
    return render_template('influencer_register.html')


#INFLUENCER LOGIN
@app.route('/influencerlogin', methods=['GET', 'POST'])
def influencer_login():
    if request.method == 'POST':
        u_name = request.form.get("u_name")
        pwd = request.form.get("pwd")
        this_influencer = User.query.filter_by(username=u_name).first()
        if not this_influencer:
            return render_template('influencer_login.html', error="Influencer does not exist.")
        if not Influencer.query.filter_by(influencer_id=this_influencer.id, password=pwd).first():
            return render_template('influencer_login.html', error="Incorrect password.")
        influencer = Influencer.query.filter_by(influencer_id=this_influencer.id).first()
        if influencer.flagged == 1:
            return render_template('influencer_login.html', error="Your account has been flagged and you cannot log in.")
        if this_influencer.user_role == 2:
            login_user(this_influencer)
            user_id = current_user.id
            user = User.query.get(user_id)
            adrequests = (db.session.query(Adrequests).join(Campaigns, Adrequests.campaign_id == Campaigns.id).filter(
                Adrequests.influencer_id == influencer.id,
                Adrequests.status.in_(["Requested to Influencer", "Accepted by Influencer"]),Campaigns.flagged == 0).all())
            influencer_details = {
                "name": influencer.name,
                "id": influencer.id,
                "category": influencer.category,
                "reach": influencer.reach,
                "niche": influencer.niche,
                "platform": influencer.platform,
            }
        accepted_by_influencer = (db.session.query(Adrequests).join(Campaigns, Adrequests.campaign_id == Campaigns.id)
        .join(Sponsor, Campaigns.sponsor_id == Sponsor.sponsor_id).filter(
            Adrequests.influencer_id == influencer.id,
            Adrequests.status == "Accepted by Influencer",Campaigns.flagged == 0,Sponsor.flagged == 0).all())
    
        accepted_by_sponsor = (db.session.query(Adrequests).join(Campaigns, Adrequests.campaign_id == Campaigns.id)
        .join(Sponsor, Campaigns.sponsor_id == Sponsor.sponsor_id).filter(
            Adrequests.influencer_id == influencer.id,Adrequests.status == "Accepted by Sponsor",
            Campaigns.flagged == 0,Sponsor.flagged == 0).all())
            # accepted_by_influencer = (db.session.query(Adrequests).join(Campaigns, Adrequests.campaign_id == Campaigns.id).filter(
            #     Adrequests.influencer_id == influencer.id,
            #     Adrequests.status == "Accepted by Influencer",
            #     Campaigns.flagged == 0).all())
            # accepted_by_sponsor = (db.session.query(Adrequests).join(Campaigns, Adrequests.campaign_id == Campaigns.id)
            #     .filter(Adrequests.influencer_id == influencer.id,
            #         Adrequests.status == "Accepted by Sponsor",
            #         Campaigns.flagged == 0).all())
            # adrequest_of_influencer = get_active_ad_requests(influencer.id)
            # adrequest_of_influencer = [ adrequest for adrequest in adrequests 
            # if adrequest.status == "Accepted by Influencer" and calculate_campaign_progress(adrequest.campaigns.start_date, adrequest.campaigns.end_date) < 100]
        return render_template('influencer_dashboard.html', u_name=u_name, id=User.id, influencer=influencer_details,
                                   active_adrequests=accepted_by_sponsor+accepted_by_influencer, adrequests=adrequests,
                                   calculate_campaign_progress=calculate_campaign_progress)
    
    return render_template('influencer_login.html')


#INFLUENCER VIEW  ALL CAMPAIGNS 
@app.route('/find_campaigns')
def find_campaigns():
    # campaigns = Campaigns.query.filter_by(visibility='public',flagged=0).all()
    campaigns = [campaign for campaign in Campaigns.query.filter_by(visibility='public', flagged=0).all()
                 if calculate_campaign_progress(campaign.start_date, campaign.end_date) < 100]
    return render_template('influencer_available_campaign.html', campaigns=campaigns)


#INFLUENCER UPDATE PROFILE
@app.route('/influencer_update_profile/<int:influencer_id>', methods=['GET', 'POST'])
@login_required
def influencer_update_profile(influencer_id):
    influencer = Influencer.query.get(influencer_id)
    if request.method == 'POST':
        category = request.form.get("category")
        niche = request.form.get("niche")
        reach = int(request.form.get("reach"))
        platform = request.form.get("platform")
        print(category)
        if reach < 0:
            return render_template('influencer_update_profile.html',influencer=influencer, error="Reach must be greater than or equal to 0.")
        else:
            influencer.category = category
            influencer.niche = niche
            influencer.reach = reach
            influencer.platform = platform
            db.session.commit()
            return redirect(url_for('influencer_dash'))
    return render_template('influencer_update_profile.html', influencer=influencer)


#INFLUENCER SEARCH CAMPAIGN
@app.route('/search_campaign',methods=['GET','POST'])
def search_campaign():
    search_query = request.form.get('search')
    campaigns=[]
    if search_query:
        campaigns = Campaigns.query.filter(
        (Campaigns.name.ilike(f'%{search_query}%')) |
        (Campaigns.niche.ilike(f'%{search_query}%')) |
        (Campaigns.description.ilike(f'%{search_query}%')) |
        (Campaigns.goals.ilike(f'%{search_query}%')),
        Campaigns.flagged != 1,
        Campaigns.visibility != 'private'
        ).all()
    return render_template('sponsor_search_result.html', campaigns=campaigns)


# INFLUENCER SENDING AD REQUEST 
@app.route('/influencer_adrequest/<int:campaign_id>', methods=['GET', 'POST'])
@login_required
def influencer_request(campaign_id):
    campaign = Campaigns.query.get(campaign_id)
    if request.method == 'POST':
        messages = request.form.get('messages')
        requirements = request.form.get('requirements')
        status = "Requested to Sponsor"
        payment_amt = int(request.form.get('payment_amt'))
        user_id = current_user.id
        user = User.query.get(user_id)
        influencer = Influencer.query.filter_by(influencer_id = user.id).first()
        if payment_amt <= 0:
            return render_template('influencer_adrequest.html', campaign=campaign, error="Payment amount must be greater than 0.")
        else:
            new_request = Adrequests(
                messages=messages,
                requirements=requirements,
                status=status,
                payment_amt=payment_amt,
                campaign_id=campaign.id,
                influencer_id=influencer.id,
                sent_by_sponsor = False
            )
            db.session.add(new_request)
            db.session.commit()
            return redirect(url_for('find_campaigns'))
    return render_template('influencer_adrequest.html', campaign=campaign)


#INFLUENCER EDITING AD REQUEST
@app.route('/influ_edit_adrequest/<int:adrequest_id>', methods=['GET', 'POST'])
def influ_edit_adrequest(adrequest_id):
    adrequest = Adrequests.query.get(adrequest_id)
    if request.method == 'POST':
        adrequest.messages = request.form.get('messages')
        adrequest.requirements = request.form.get('requirements')
        adrequest.payment_amt = int(request.form.get('payment_amt'))
        if adrequest.payment_amt <= 0:
            return render_template('influencer_edit_adrequest.html', adrequest=adrequest, error="Payment amount must be greater than 0.")
        db.session.commit()
        return redirect(url_for('influencer_view_campaign', campaign_id=adrequest.campaign_id))
    return render_template('influencer_edit_adrequest.html', adrequest=adrequest)


#INFLUENCER DELETING AD REQUEST
@app.route('/infl_del_ad/<int:adrequest_id>', methods=['GET','POST'])
def infl_del_ad(adrequest_id):
    adrequest = Adrequests.query.get(adrequest_id)
    if adrequest:
        db.session.delete(adrequest)
        db.session.commit()
    return redirect(url_for('influencer_view_campaign', campaign_id=adrequest.campaign_id))



#INFLUENCER DASHBOARD
@app.route('/influencer_dash',methods = ['GET','POST'])
def influencer_dash():
    u_name = current_user.username
    user_id = current_user.id
    user = User.query.get(user_id)
    influencer = Influencer.query.filter_by(influencer_id = user.id).first()
    adrequests = (
        db.session.query(Adrequests).join(Campaigns, Adrequests.campaign_id == Campaigns.id).filter(
            Adrequests.influencer_id == influencer.id,
            Adrequests.status.in_(["Requested to Influencer", "Accepted by Influencer"]),
            Campaigns.flagged == 0).all())
    influencer_details = {
                        "name": influencer.name,
                        "id": influencer.id,
                        "category": influencer.category,
                        "reach": influencer.reach,
                        "niche": influencer.niche,
                        "platform": influencer.platform,
                    }
    accepted_by_influencer = (db.session.query(Adrequests).join(Campaigns, Adrequests.campaign_id == Campaigns.id)
        .join(Sponsor, Campaigns.sponsor_id == Sponsor.sponsor_id).filter(
            Adrequests.influencer_id == influencer.id,
            Adrequests.status == "Accepted by Influencer",Campaigns.flagged == 0,Sponsor.flagged == 0).all())
    
    accepted_by_sponsor = (db.session.query(Adrequests).join(Campaigns, Adrequests.campaign_id == Campaigns.id)
        .join(Sponsor, Campaigns.sponsor_id == Sponsor.sponsor_id).filter(
            Adrequests.influencer_id == influencer.id,Adrequests.status == "Accepted by Sponsor",
            Campaigns.flagged == 0,Sponsor.flagged == 0).all())
    # accepted_by_influencer = (db.session.query(Adrequests).join(Campaigns, Adrequests.campaign_id == Campaigns.id).filter(
    #             Adrequests.influencer_id == influencer.id,
    #             Adrequests.status == "Accepted by Influencer",
    #             Campaigns.flagged == 0).all())
    # accepted_by_sponsor = (db.session.query(Adrequests).join(Campaigns, Adrequests.campaign_id == Campaigns.id)
    #     .filter(Adrequests.influencer_id == influencer.id,
    #         Adrequests.status == "Accepted by Sponsor",
    #         Campaigns.flagged == 0).all())
    # adrequest_of_influecner = get_active_ad_requests(influencer.id)
    # OLD adrequest_of_influencer = [ adrequest for adrequest in adrequests 
    #     if adrequest.status == "Accepted by Influencer" and calculate_campaign_progress(adrequest.campaigns.start_date, adrequest.campaigns.end_date) < 100]
    return render_template('influencer_dashboard.html', u_name=u_name, id = User.id, influencer=influencer_details,active_adrequests = accepted_by_influencer+accepted_by_sponsor,
                           adrequests = adrequests, calculate_campaign_progress=calculate_campaign_progress)



#INFLUENCER VIEW ADREQUEST FROM DASHBOARD (SENT BY SPONSOR)
@app.route('/influencer_view_adrequest/<int:adrequest_id>', methods=['GET','POST'])
def influencer_view_adrequest(adrequest_id):
    # adrequest = Adrequests.query.get(adrequest_id)
    adrequest = (
        db.session.query(Adrequests, Campaigns, Sponsor).join(Campaigns, Adrequests.campaign_id == Campaigns.id)
        .join(Sponsor, Campaigns.sponsor_id == Sponsor.sponsor_id).filter(Adrequests.id == adrequest_id).first())
    adrequest_data, campaign_data, sponsor_data = adrequest
    return render_template('influencer_view_adrequest.html', adrequest=adrequest_data,sponsor = sponsor_data)


#INFLUENCER STATISTICS
@app.route('/influencer_stats')
@login_required
def influencer_stats():
    user_id = current_user.id
    user = User.query.get(user_id)
    influencer = Influencer.query.filter_by(influencer_id=user.id).first()
    total_adrequests = Adrequests.query.filter_by(influencer_id=influencer.id).count()
    accepted_adrequests = Adrequests.query.filter_by(influencer_id=influencer.id, status='Accepted by Influencer').count()
    ongoing_campaigns = Campaigns.query.join(Adrequests).filter(Adrequests.influencer_id == influencer.id, 
                                                                Adrequests.status.in_(['Accepted by Influencer','Accepted by Sponsor']),
                                                                # Adrequests.status == 'Accepted by Influencer',
                                                                Campaigns.end_date > datetime.now(),  Campaigns.start_date <= datetime.now(),
                                                                Campaigns.flagged == 0).count()
    # ongoing_campaigns = db.session.query(Campaigns).join(Adrequests).join(Sponsor).filter(
    #     Adrequests.influencer_id == influencer.id, 
    #     Adrequests.status.in_(['Accepted by Influencer', 'Accepted by Sponsor']),
    #     Campaigns.end_date > datetime.now(),
    #     Campaigns.start_date <= datetime.now(),
    #     Campaigns.flagged == 0,
    #     Sponsor.flagged == 0
    # ).count()
    all_campaigns = Campaigns.query.join(Adrequests).filter(Adrequests.influencer_id == influencer.id).all()
    completed_campaigns = sum(1 for campaign in all_campaigns if calculate_campaign_progress(campaign.start_date, campaign.end_date) >= 100)

    return render_template('influencer_statistics.html', 
                           total_adrequests=total_adrequests, 
                           accepted_adrequests=accepted_adrequests, 
                           ongoing_campaigns=ongoing_campaigns,
                           completed_campaigns=completed_campaigns)


#INFLUENCER ACCEPTING AD REQUESTS
@app.route('/influencer_accept_adrequest/<int:adrequest_id>', methods=['GET','POST'])
def influencer_accept_adrequest(adrequest_id):
    adrequest = Adrequests.query.get(adrequest_id)
    if adrequest:
        adrequest.status = "Accepted by Influencer"
        db.session.commit()
    return redirect(url_for('influencer_dash'))


#INFLUENCER REJECTING AD REQUESTS
@app.route('/influencer_reject_adrequest/<int:adrequest_id>', methods=['GET','POST'])
def influencer_reject_adrequest(adrequest_id):
    adrequest = Adrequests.query.get(adrequest_id)
    if adrequest:
        if adrequest.status in ["Requested to Influencer", "Accepted by Influencer"]:
            adrequest.status = "Rejected by Influencer"
            db.session.commit()
    return redirect(url_for('influencer_dash'))

#INFLUENCER VIEW SPECIFIC CAMPAIGN
@app.route('/influencer_view_campaign/<int:campaign_id>')
@login_required #new
def influencer_view_campaign(campaign_id):
    # campaign = Campaigns.query.get(campaign_id)
    # sponsor = Sponsor.query.get(campaign.sponsor_id)
    campaign_data = db.session.query(Campaigns, Sponsor).join(Sponsor, Campaigns.sponsor_id == Sponsor.sponsor_id).filter(Campaigns.id == campaign_id).first()
    campaign, sponsor = campaign_data
    # adrequests = Adrequests.query.filter_by(campaign_id=campaign_id, sent_by_sponsor = False, influencer_id=current_user.id).all()
    adrequests = db.session.query(Adrequests).join(Influencer).filter(
        Adrequests.campaign_id == campaign_id,
        Adrequests.sent_by_sponsor == False,
        Influencer.influencer_id == current_user.id
    ).all()
    # user_id = current_user.id #new
    # influencer = Influencer.query.filter_by(influencer_id=user_id).first() #new 
    # adrequests = Adrequests.query.filter_by(campaign_id=campaign_id,
    #                                          status="Requested to Sponsor" or "Accepted by Sponsor".all()) #new
    return render_template('influencer_view_campaign.html', campaign=campaign,sponsor = sponsor, adrequests=adrequests)


#---------SPONSOR--------

#SPONSOR GETTING ALL CAMPAIGNS CREATED AND VIEWING
@app.route('/sponsor_campaign', methods = ['GET','POST'])
def sponsor_campaign():
    # sponsor_id = Sponsor.id
    this_id =  current_user.id
    sponsor = Sponsor.query.filter_by(sponsor_id = this_id).first()
    if sponsor:
        campaigns = Campaigns.query.filter_by(sponsor_id=this_id, flagged=0).all()
    return render_template('sponsor_campaign.html', campaigns = campaigns, sponsor = sponsor,calculate_campaign_progress=calculate_campaign_progress)

# @app.route('/sponsor_campaign', methods = ['GET','POST'])
# def sponsor_campaign():
#     # sponsor_id = Sponsor.id
#     this_id =  current_user.id
#     sponsor = Sponsor.query.filter_by(sponsor_id = this_id).first()
#     cam = sponsor.campaigns
#     return render_template('sponsor_campaign.html', campaigns = cam, sponsor = sponsor)


#SPONSOR LOGOUT
@app.route('/sponsor_logout')
@login_required
def sponsor_logout():
    logout_user()
    return render_template('sponsor_login.html')

#SPONSOR DASHBOARD
@app.route('/sponsor_dash',methods = ['GET','POST'])
def sponsor_dash():
    user_id = current_user.id
    user = User.query.get(user_id)
    sponsor = Sponsor.query.filter_by(sponsor_id = user.id).first()
    adrequests = db.session.query(Adrequests).join(Campaigns).join(Influencer).filter(
        Campaigns.sponsor_id == sponsor.sponsor_id,
        Campaigns.flagged == 0,
        Influencer.flagged == 0,
        Adrequests.status.in_(["Requested to Sponsor", "Accepted by Sponsor"])
    ).all()
    # adrequests = db.session.query(Adrequests).join(Campaigns).filter(Campaigns.sponsor_id == sponsor.sponsor_id,Campaigns.flagged == 0,
    # Adrequests.status.in_(["Requested to Sponsor", "Accepted by Sponsor"])).all()
    campaigns = Campaigns.query.filter_by(sponsor_id = sponsor.sponsor_id,flagged=0).all()
    active_campaigns=[]
    for campaign in campaigns:
        if(campaign_isactive(campaign.start_date,campaign.end_date,date.today())):
            active_campaigns.append(campaign)
    return render_template('sponsor_dashboard.html', adrequests=adrequests, u_name=current_user.username, id = User.id, 
                           campaigns=active_campaigns, calculate_campaign_progress=calculate_campaign_progress)
    # u_name = current_user.username 
    # user_id = current_user.id
    # sponsor = Sponsor.query.filter_by(sponsor_id = user_id).first()
    # adrequests = db.session.query(Adrequests).join(Campaigns).filter(Campaigns.sponsor_id == sponsor.id).all()
    # return render_template('sponsor_dashboard.html', u_name = u_name, adrequests = adrequests, id = User.id)


#SPONSOR REGISTER
@app.route('/sponsorregister' , methods = ['GET','POST'])
def sponsor_reg():
    if request.method == 'POST':
        u_name = request.form.get("u_name")
        pwd = request.form.get("pwd")
        c_name = request.form.get("c_name")
        c_budget = int(request.form.get("c_budget"))
        industry = request.form.get("industry")
        if c_budget < 0:
            return render_template('sponsor_register.html', message="Budget must be greater than 0.")
        if not (u_name and pwd and c_name and c_budget and industry):
            return render_template('sponsor_register.html', message="Please fill out all fields and try again.")
        this_sponsor = Sponsor.query.filter_by(username = u_name).first()
        if this_sponsor:
            return "sponsor already exists"
        else:
            new_user = User(username = u_name, user_role = 1)
            db.session.add(new_user)
            db.session.commit()
            new_sponsor = Sponsor(company_name = c_name, company_budget = c_budget, username = u_name, password = pwd, industry = industry,sponsor_id = new_user.id)
            db.session.add(new_sponsor)
            db.session.commit()
            return redirect('/sponsorlogin')
    return render_template('sponsor_register.html')


#VEWING ADREQUEST
@app.route('/sponsor_view_adrequest/<int:adrequest_id>', methods=['GET','POST'])
def sponsor_view_adrequest(adrequest_id):
    adrequest = Adrequests.query.get(adrequest_id)
    return render_template('sponsor_view_adrequest.html', adrequest=adrequest)


#SPONSOR ACCEPTING AD REQUEST
@app.route('/sponsor_accept_adrequest/<int:adrequest_id>', methods=['GET','POST'])
def sponsor_accept_adrequest(adrequest_id):
    adrequest = Adrequests.query.get(adrequest_id)
    if adrequest:
        adrequest.status = "Accepted by Sponsor"
        db.session.commit()
    return redirect(url_for('sponsor_dash'))


#SPONSOR REJECTING AD REQUESTS
@app.route('/sponsor_reject_adrequest/<int:adrequest_id>', methods=['GET','POST'])
def sponsor_reject_adrequest(adrequest_id):
    adrequest = Adrequests.query.get(adrequest_id)
    if adrequest:
        if adrequest.status in ["Accepted by Sponsor","Requested to Sponsor"]:
            adrequest.status = "Rejected by Sponsor"
            db.session.commit()
    return redirect(url_for('sponsor_dash'))

#SPONSOR LOGIN
@app.route('/sponsorlogin', methods=['GET', 'POST'])
def sponsor_login():
    if request.method == 'POST':
        u_name = request.form.get("u_name")
        pwd = request.form.get("pwd")
        this_sponsor = User.query.filter_by(username=u_name).first()
        if not this_sponsor:
            return render_template('sponsor_login.html', error="Sponsor does not exist.")
        if this_sponsor:
            if Sponsor.query.filter_by(password=pwd).all():
                sponsor = Sponsor.query.filter_by(sponsor_id=this_sponsor.id).first()
                if sponsor.flagged == 1:
                    return render_template('sponsor_login.html', error="Your account has been flagged and you cannot log in.")
                if this_sponsor.user_role == 1:
                    login_user(this_sponsor)
                    user_id = current_user.id
                    user = User.query.get(user_id)
                    sponsor_id = user_id
                    campaigns = Campaigns.query.filter_by(sponsor_id=sponsor.sponsor_id, flagged=0).all()
                    active_campaigns = []
                    for campaign in campaigns:
                        if campaign_isactive(campaign.start_date, campaign.end_date, date.today()):
                            active_campaigns.append(campaign)
                    adrequests = []
                    adrequests = db.session.query(Adrequests).join(Campaigns).join(Influencer).filter(
                        Campaigns.sponsor_id == sponsor.sponsor_id,
                        Campaigns.flagged == 0,
                        Influencer.flagged == 0,
                        Adrequests.status.in_(["Requested to Sponsor", "Accepted by Sponsor"])).all()
                    return render_template('sponsor_dashboard.html', adrequests=adrequests, u_name=current_user.username, id=user.id,
                                           campaigns=active_campaigns, calculate_campaign_progress=calculate_campaign_progress)
    
    return render_template('sponsor_login.html')

# @app.route('/sponsorlogin' , methods = ['GET','POST'])
# def sponsor_login():
#     if request.method == 'POST':
#         u_name = request.form.get("u_name")
#         pwd = request.form.get("pwd")
#         this_sponsor = User.query.filter_by(username = u_name).first()
#         if not this_sponsor:
#             return render_template('sponsor_login.html', error="Sponsor does not exist.")
#         if this_sponsor:
#             if(Sponsor.query.filter_by(password = pwd).all()):
#                 sponsor = Sponsor.query.filter_by(sponsor_id=this_sponsor.id).first()
#                 if sponsor.flagged == 1:
#                     return render_template('sponsor_login.html', error="Your account has been flagged and you cannot log in.")
#                 if(this_sponsor.user_role == 1):
#                     login_user(this_sponsor)
#                     user_id = current_user.id
#                     user = User.query.get(user_id)
#                     sponsor_id = user_id
#                     campaigns = Campaigns.query.filter_by(sponsor_id = sponsor.sponsor_id,flagged=0).all()
#                     active_campaigns=[]
#                     for campaign in campaigns:
#                         if(campaign_isactive(campaign.start_date,campaign.end_date,date.today())):
#                                 active_campaigns.append(campaign)
#                         adrequests=[]     
#                         adrequests = db.session.query(Adrequests).join(Campaigns).join(Influencer).filter(
#                         Campaigns.sponsor_id == sponsor.sponsor_id,Campaigns.flagged == 0,Influencer.flagged == 0,
#                         Adrequests.status.in_(["Requested to Sponsor", "Accepted by Sponsor"])).all()
#                     # adrequests = db.session.query(Adrequests).join(Campaigns).filter(Campaigns.sponsor_id == sponsor.sponsor_id,
#                     #                                                                  Campaigns.flagged == 0,
#                     # Adrequests.status.in_(["Requested to Sponsor", "Accepted by Sponsor"])).all()
#                     return render_template('sponsor_dashboard.html', adrequests=adrequests, u_name=current_user.username, id = User.id,
#                                            campaigns=active_campaigns, calculate_campaign_progress=calculate_campaign_progress)
#     return render_template('sponsor_login.html')


# SPONSOR SEARCH FOR INFLUENCER
@app.route('/search_influencer', methods=['GET','POST'])
def search_influencer():
    search_query = request.form.get('search')
    influencers = []
    if search_query:
        influencers = Influencer.query.filter(
        (Influencer.name.ilike(f'%{search_query}%')) |
        (Influencer.category.ilike(f'%{search_query}%')) |
        (Influencer.platform.ilike(f'%{search_query}%')) |
        (Influencer.niche.ilike(f'%{search_query}%')),
        Influencer.flagged != 1 
        ).all()
    return render_template('influencer_search_result.html', influencers=influencers)


#-------HOME---------
# @app.route('/home' , methods = ['GET','POST'])
# def home():
#     return render_template('home.html')
@app.route('/' , methods = ['GET','POST'])
def home():
    return render_template('home.html')




#ADMIN OVERALL STATISTICS
@app.route('/admin_stats')
def admin_stats():
    sponsor = Sponsor.query.all()
    influencer = Influencer.query.all()
    all_campaigns = Campaigns.query.all()
    adrequests = Adrequests.query.all()
    num_sponsors = len(sponsor)
    num_influencers = len(influencer)
    all_campaigns = len(all_campaigns)
    num_adrequests = len(adrequests)
    plt.clf()
    categories = ['Sponsors', 'Influencers', 'Campaigns','Ad Requests']
    counts = [num_sponsors, num_influencers, all_campaigns,num_adrequests]
    plt.bar(categories, counts, color=['blue', 'green', 'orange', 'red'])
    plt.xlabel('Categories')
    plt.ylabel('Count')
    plt.title('Number of Sponsors, Influencers, Campaigns, Adrequests')
    ax = plt.gca()
    ax.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))
    plt.xticks(ticks=range(len(categories)), labels=categories)
    plt.savefig('static/admin_stats.png')
    return render_template("admin_statistics.html")

#ADMIN INFLUENCER STATISTICS
@app.route('/admin_influ_stats')
def admin_influ_stats():
    influencer = Influencer.query.all()
    infl_data=[]
    infl_catg=[]
    infl_platform=[]
    max_reach_influencer = max(influencer, key=lambda i: i.reach)
    max_reach_name = max_reach_influencer.name
    flagged_counts = sum(1 for i in influencer if i.flagged == 1)
    non_flagged_counts = len(influencer) - flagged_counts
    for i in influencer:
        infl_data.append(i.reach)
        infl_catg.append(i.category)
        infl_platform.append(i.platform)
    num_influencers = len(influencer)
    category_counts = Counter(infl_catg)
    platform_counts = Counter(infl_platform)
    plt.clf()
    plt.figure(figsize=(5, 5))
    plt.hist(infl_data, bins=10, edgecolor='black')
    plt.xlabel('Reach/Followers')
    plt.ylabel('Number of Influencers')
    plt.title('Distribution of Influencers by Reach')
    ax = plt.gca()
    ax.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))
    bin_edges = plt.hist(infl_data, bins=10, edgecolor='black')[1]
    plt.xticks(bin_edges, rotation=45)
    plt.tight_layout()
    plt.savefig('static/influ_reach.png')

    plt.clf()
    plt.bar(category_counts.keys(), category_counts.values(), color='grey')
    plt.xlabel('Category')
    plt.ylabel('Number of Influencers')
    plt.title('Number of Influencers by Category')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    ax = plt.gca()
    ax.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))
    plt.savefig('static/influ_category.png')

    plt.clf()
    plt.bar(platform_counts.keys(), platform_counts.values(), color='orange')
    plt.xlabel('Platform')
    plt.ylabel('Number of Influencers')
    plt.title('Number of Influencers by Platform')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    ax = plt.gca()
    ax.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))
    plt.savefig('static/influ_platform.png')

    plt.clf()
    plt.pie([flagged_counts, non_flagged_counts], labels=['Flagged', 'Non-Flagged'], autopct='%1.1f%%', colors=['red', 'limegreen'])
    plt.title('Flagged vs Non-Flagged Influencers')
    plt.savefig('static/influ_flag.png')
    return render_template('admin_influencer_stats.html',max_reach_name=max_reach_name)

#ADMIN SPONSOR STATISTICS
@app.route('/admin_spon_stats')
def admin_spon_stats():
    sponsors = Sponsor.query.all()
    sponsor_names = [sponsor.username for sponsor in sponsors]
    campaign_counts = [Campaigns.query.filter_by(sponsor_id=sponsor.sponsor_id).count() for sponsor in sponsors]
    # campaign_counts = [len(sponsor.campaigns) for sponsor in sponsors]
    com_budget=[]
    industries=[]
    industries = [sponsor.industry for sponsor in sponsors]
    industry_count = Counter(industries)
    flagged_counts = sum([1 for sponsor in sponsors if sponsor.flagged == 1])
    non_flagged_counts = len(sponsors) - flagged_counts
    for i in sponsors:
        com_budget.append(float(i.company_budget))
    plt.clf()
    n, bins, patches = plt.hist(com_budget, bins=10, edgecolor='black')
    # plt.hist(com_budget, bins=10, edgecolor='black')
    plt.xlabel('Company Budget')
    plt.ylabel('Number of Sponsors')
    plt.title('Distribution of Company Budgets among Sponsors')
    ax = plt.gca()
    ax.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))
    ax.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))
    plt.xticks(bins, rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig('static/spon_cbudget.png')

    plt.clf()
    plt.figure(figsize=(6, 6))
    plt.pie([flagged_counts, non_flagged_counts], labels=['Flagged', 'Non-Flagged'], autopct='%1.1f%%', colors=['red', 'limegreen'])
    plt.title('Flagged vs Non-Flagged Sponsors')
    plt.savefig('static/spon_flag-nflag.png')

    plt.clf()
    plt.bar(industry_count.keys(), industry_count.values(), color='blue')
    plt.xlabel('Industry')
    plt.ylabel('Number of Sponsors')
    plt.title('Number of Sponsors per Industry')
    plt.xticks(rotation=45)
    plt.tight_layout()
    ax = plt.gca()
    ax.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))
    plt.savefig('static/spon_per_industry.png')

    plt.clf()
    plt.bar(sponsor_names, campaign_counts, color='skyblue')
    plt.xlabel('Sponsor Name')
    plt.ylabel('Number of Campaigns')
    plt.title('Number of Campaigns Created by Each Sponsor')
    plt.xticks(rotation=45, ha='right') 
    plt.tight_layout() 
    ax = plt.gca()
    ax.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))
    plt.savefig('static/sponsor_campaigns.png')
    return render_template('admin_sponsor_stats.html')

#ADMIN CAMPAIGN STATS
@app.route('/admin_cam_stats')
def admin_campaign_stats():
    campaigns = Campaigns.query.all()
    visibilities = [c.visibility for c in campaigns]
    visibility_counts = Counter(visibilities)
    campaign_budgets = [c.campaign_budget for c in campaigns]
    campaign_durations = [(c.end_date - c.start_date).days for c in campaigns]
    flagged_counts = sum(1 for c in campaigns if c.flagged == 1)
    non_flagged_counts = len(campaigns) - flagged_counts
    plt.clf()
    n, bins, patches = plt.hist(campaign_budgets, bins=10, edgecolor='black')
    # plt.hist(campaign_budgets, bins=10, edgecolor='black')
    plt.xlabel('Campaign Budget')
    plt.ylabel('Number of Campaigns')
    plt.title('Distribution of Campaign Budgets')
    ax = plt.gca()
    ax.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))
    plt.xticks(bins, rotation=45)
    plt.tight_layout()
    plt.savefig('static/campaign_budget_distribution.png') 

    plt.clf()
    plt.pie([flagged_counts, non_flagged_counts], labels=['Flagged', 'Non-Flagged'], autopct='%1.1f%%', colors=['red', 'limegreen'])
    plt.title('Flagged vs Non-Flagged Campaigns')
    plt.savefig('static/cam_flag_nflag.png')

    # plt.clf()
    # n, bins, patches = plt.hist(campaign_durations, bins=10, edgecolor='black')
    # # plt.hist(campaign_durations, bins=10, edgecolor='black')
    # plt.xlabel('Duration (days)')
    # plt.ylabel('Number of Campaigns')
    # plt.title('Distribution of Campaign Durations')
    # ax = plt.gca()
    # ax.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))
    # ax.xaxis.set_major_locator(ticker.MaxNLocator(integer=True))
    # # plt.xticks(bins,rotation=45, ha='right')
    # plt.xticks(range(min(campaign_durations), max(campaign_durations) + 2, max(1, (max(campaign_durations) - min(campaign_durations)) // 10)))
    # # plt.xticks(range(min(campaign_durations), max(campaign_durations) + 2))
    # plt.tight_layout()
    # plt.savefig('static/campaign_duration_distribution.png')
    
    plt.clf()
    plt.pie(visibility_counts.values(), labels=visibility_counts.keys(), autopct='%1.1f%%', colors=['blue', 'orange'])
    plt.title('Public vs Private Campaigns')
    plt.savefig('static/campaign_visibility_distribution.png')
    return render_template('admin_campaign_stats.html')