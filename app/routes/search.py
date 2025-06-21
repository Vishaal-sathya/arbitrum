from flask import redirect, render_template, url_for, flash, request, Blueprint
from flask_login import current_user, login_required
from app.extensions import db
from app.models import User,Skills, UserSkills, Profile, Endorsement
from fuzzywuzzy import fuzz


search_bp = Blueprint('search', __name__)



@search_bp.route('/search', methods=['GET'])
def search_page():
    from fuzzywuzzy import fuzz

    query = request.args.get('q', '').strip().lower()
    college_query = request.args.get('college', '').strip().lower()
    skill_query = request.args.get('skill', '').strip().lower()

    users = User.query.all()
    matched_users = []

    for user in users:
        username_match = not query or fuzz.partial_ratio(query, user.username.lower()) > 60

        college_match = True
        if college_query:
            if user.profile and user.profile.college:
                college_match = fuzz.partial_ratio(college_query, user.profile.college.lower()) > 80
            else:
                college_match = False

        skill_match = True
        if skill_query:
            if user.skills:
                skill_match = any(s.skill.skill.strip().lower() == skill_query for s in user.skills)
            else:
                skill_match = False

        if username_match and college_match and skill_match:
            matched_users.append(user)

    return render_template('search/search.html', users=matched_users)




