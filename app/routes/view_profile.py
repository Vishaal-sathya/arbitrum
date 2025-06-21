from flask import Blueprint, request, flash, render_template, redirect, current_app, send_file, abort, url_for
from flask_login import login_required, current_user
from utils.decorators import role_required
from app.extensions import db
from app.models import User, Skills, UserSkills, Profile, Endorsement
from sqlalchemy import and_
import os
from collections import Counter

view_profile_bp = Blueprint("view_profile", __name__)

@view_profile_bp.route('/view_profile/<int:user_id>')
def view_profile(user_id):
    user = User.query.get(user_id)
    profile = user.profile
    skills = user.skills
    projects = user.projects
    experiences = user.experiences
    educations = user.education
    languages = user.languages
    endorsement = Endorsement.query.filter(
        and_(
            Endorsement.user_id == user_id,  
            Endorsement.endorsed_by == current_user.id, 
        )
    ).first()
    if endorsement:
        endorsed_skill = endorsement.skill.skill
    else:
        endorsed_skill = ""

    all_endorsements = Endorsement.query.filter_by(user_id=user_id)
    endorsement_list = []
    if all_endorsements:
        endorsement_list = [endorsement_.skill.skill for endorsement_ in all_endorsements]
        endorsement_count = Counter(endorsement_list)
        try:
            print(endorsement_count)
        except:
            pass
        

    return render_template('view_profile/view_profile.html',
                           current_user=current_user,
                           user=user,
                           profile=profile,
                           skills=skills,
                           projects=projects,
                           experiences=experiences,
                           educations=educations,
                           languages=languages,
                           endorsed_skill=endorsed_skill,
                           endorsement_counter=endorsement_count
                           )
    
@view_profile_bp.route('/downloadcv/<int:user_id>', methods=['GET','POST'])
def download_cv(user_id):
    user = User.query.get(user_id)
    resume = user.profile.resume
    resume_path = os.path.join(current_app.root_path,'static/resumes',resume)
    if not resume_path or not os.path.exists(resume_path):
        abort(404,description='resume not found')
    return send_file(resume_path, as_attachment=True)

@view_profile_bp.route('/endorse/<int:user_id>/<int:skill_id>', methods=['GET','POST'])
def endorse_skill(user_id, skill_id):
    endorsement = Endorsement.query.filter(
        and_(
            Endorsement.user_id == user_id,  
            Endorsement.endorsed_by == current_user.id, 
        )
    ).first()
    # print(endorsement.skill.skill)
    if endorsement:
        flash("You've already endorsed this user")
    else:
        new_endorsement = Endorsement(
            user_id=user_id,
            endorsed_by=current_user.id,
            skill_id=skill_id
        )
        db.session.add(new_endorsement)
        db.session.commit()
    return redirect(url_for("view_profile.view_profile",user_id=user_id))

@view_profile_bp.route('/remove_endorse/<int:user_id>/<int:skill_id>', methods=['GET', 'POST'])
def remove_endorsement(user_id, skill_id):
    endorsement = Endorsement.query.filter(
        and_(
            Endorsement.user_id == user_id,  # user who gave the endorsement
            Endorsement.endorsed_by == current_user.id,  # currently logged-in user
            Endorsement.skill_id == skill_id
        )
    ).first()

    if endorsement:
        db.session.delete(endorsement)
        db.session.commit()
    return redirect(url_for("view_profile.view_profile",user_id=user_id))