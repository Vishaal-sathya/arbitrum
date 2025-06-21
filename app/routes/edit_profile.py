from flask import Blueprint, request, redirect, url_for, render_template, current_app, flash
from app.models import User, Profile, Skills, Languages, Projects, Experience, UserLanguages, UserSkills, Education, Endorsement
from app.extensions import db
from app.forms import ProfileForm, SkillsForm, LanguagesForm, ProjectForm, ExperienceForm, EducationForm
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
import os
import json
from sqlalchemy import and_
import base64
from io import BytesIO
from PIL import Image


edit_profile_bp = Blueprint('profile', __name__)

@edit_profile_bp.route('/updateprofile',methods=['GET','POST'])
@login_required
def update_profile():
    profile_form = ProfileForm(obj=current_user.profile)
    
    skills_form = SkillsForm()
    if not skills_form.submit_skills.data:
        skills = [us.skill.skill for us in current_user.skills]
        skills_form.skills.data = json.dumps([{"value": skill} for skill in skills])

    languages_form = LanguagesForm()
    if not languages_form.submit_languages.data:
        languages = [ul.language.language for ul in current_user.languages]
        languages_form.languages.data = json.dumps([{"value": language} for language in languages])
    

    add_education_form = EducationForm(prefix='add')
    update_education_form = EducationForm(prefix='update')
    editing_education = None
    edit_education_id = request.args.get('edit_education',type=int)
    if edit_education_id:
        editing_education = Education.query.get(edit_education_id)
        update_education_form = EducationForm(obj=editing_education,prefix='update')

    add_project_form = ProjectForm(prefix='add')
    update_project_form = ProjectForm(prefix='update')
    editing_project = None
    edit_project_id = request.args.get('edit_project',type=int)
    if edit_project_id:
        editing_project = Projects.query.get(edit_project_id)
        update_project_form = ProjectForm(obj=editing_project, prefix='update')
    
    add_experience_form = ExperienceForm(prefix='add')
    update_experience_form = ExperienceForm(prefix='update')
    editing_experience = None
    edit_experience_id = request.args.get('edit_experience', type=int)
    if edit_experience_id:
        editing_experience = Experience.query.get(edit_experience_id)
        update_experience_form = ExperienceForm(obj=editing_experience, prefix='update')
        

    return render_template('edit_profile/edit_profile.html',
                           user=current_user,
                           profile_form=profile_form,
                           skills_form=skills_form,
                           languages_form=languages_form,
                           add_project_form=add_project_form,
                           update_project_form=update_project_form,
                           editing_project=editing_project,
                           add_experience_form=add_experience_form,
                           update_experience_form=update_experience_form,
                           editing_experience=editing_experience,
                           add_education_form=add_education_form,
                           update_education_form=update_education_form,
                           editing_education=editing_education
                           )


@edit_profile_bp.route('/updateuserprofile', methods=['POST'])
def update_user_profile():
    profile_form = request.form
    profile = Profile.query.filter_by(user_id=current_user.id).first()
    if not profile:
        profile = Profile(user_id=current_user.id)
        db.session.add(profile)

    # Update text fields
    profile.one_liner = profile_form.get('one_liner')
    profile.bio = profile_form.get('bio')
    profile.college = profile_form.get('college')
    linkedin_url = profile_form.get('linkedin_url')
    if linkedin_url and not linkedin_url.startswith(('http://', 'https://')):
        linkedin_url = 'https://' + linkedin_url
    profile.linkedin_url = linkedin_url

    github_url = profile_form.get('github_url')
    if github_url and not github_url.startswith(('http://', 'https://')):
        github_url = 'https://' + github_url
    profile.github_url = github_url

    # Handle cropped image as blob (from fetch FormData)
    cropped_data = request.form.get('cropped_photo')
    if cropped_data:
        # Remove base64 prefix
        header, encoded = cropped_data.split(",", 1)
        image_data = base64.b64decode(encoded)
        image = Image.open(BytesIO(image_data))
        filename = f'{current_user.id}_{current_user.username}_profile.png'
        file_path = os.path.join(current_app.root_path, 'static/profile_photos', filename)
        image.save(file_path)
        profile.photo = filename

    # Handle resume upload
    if request.files.get('resume'):
        resume = request.files['resume']
        filename = secure_filename(resume.filename)
        unique_filename = f'{current_user.id}_{current_user.username}_{filename}'
        file_path = os.path.join(current_app.root_path, 'static/resumes', unique_filename)
        resume.save(file_path)
        profile.resume = unique_filename

    db.session.commit()
    flash('Profile updated successfully', 'success')
    return redirect(url_for('profile.update_profile',tab='personal'))


@edit_profile_bp.route('/updateskills', methods=['GET','POST'])
def update_skills():
    skills_form = request.form
    skill_tags = json.loads(skills_form.get('skills'))
    if not skill_tags:
        flash('Please add atleast one skill')
        return redirect(url_for('profile.update_profile',tab='technical'))
    UserSkills.query.filter_by(user_id=current_user.id).delete()
    skill_ids = []
    for tag in skill_tags:
        skill_name = tag['value']
        print(skill_name)
        skill = Skills.query.filter_by(skill=skill_name).first()
        if not skill:
            skill = Skills(skill=skill_name)
            db.session.add(skill)
            db.session.flush()
        db.session.add(UserSkills(
            user_id = current_user.id,
            skill_id = skill.id
        ))
        db.session.commit()
        skill_ids.append(Skills.query.filter_by(skill=skill_name).first().id)
    
    Endorsement.query.filter(
        and_(
                Endorsement.user_id == current_user.id,
                ~Endorsement.skill_id.in_(skill_ids)  
            )
    ).delete(synchronize_session=False)

    db.session.commit()
    
    flash('Skills updated successfully','success')
    return redirect(url_for('profile.update_profile',tab='technical'))

@edit_profile_bp.route('/updatelanguages', methods=['GET','POST'])
def update_languages():
    languages_form = request.form
    language_tags = json.loads(languages_form.get('languages'))
    UserLanguages.query.filter_by(user_id=current_user.id).delete()
    for tag in language_tags:
        language_name = tag['value']
        language = Languages.query.filter_by(language=language_name).first()
        if not language:
            language = Languages(language=language_name)
            db.session.add(language)
            db.session.flush()
        db.session.add(UserLanguages(
            user_id = current_user.id,
            language_id = language.id
        ))
        db.session.commit()
    
    flash('Languages updated successfully','success')
    return redirect(url_for('profile.update_profile',tab='technical'))

@edit_profile_bp.route('/addproject',methods=['GET','POST'])
def add_project():
    form = request.form
    project = Projects(
        user_id = current_user.id,
        title = form.get('add-title'),
        description = form.get('add-description'),
        link = form.get('add-link')
    )
    db.session.add(project)
    db.session.commit()
    flash('Project Added Successfully','success')
    return redirect(url_for('profile.update_profile',tab='projects'))

@edit_profile_bp.route('/updateproject/<int:project_id>', methods=['GET','POST'])
def update_project(project_id):
    form = request.form
    project = Projects.query.get(project_id)
    project.title = form.get('update-title')
    project.description = form.get('update-description')
    project.link = form.get('update-link')
    db.session.commit()
    flash('Project updated Successfully','success')
    return redirect(url_for('profile.update_profile',tab='projects'))

@edit_profile_bp.route('/deleteproject/<int:project_id>', methods=['GET','POST'])
def delete_project(project_id):
    db.session.delete(Projects.query.get(project_id))
    db.session.commit()
    flash('Project deleted successfully','success')
    return redirect(url_for('profile.update_profile',tab='projects'))

@edit_profile_bp.route('/addexperience', methods=['GET','POST'])
def add_experience():
    form = request.form
    new_experience = Experience(
        user_id = current_user.id,
        organization_name = form.get('add-organization_name'),
        position = form.get('add-position'),
        start_date = form.get('add-start_date'),
        end_date = form.get('add-end_date')
    )
    db.session.add(new_experience)
    db.session.commit()
    flash('Experience added Successfully','success')
    return redirect(url_for('profile.update_profile',tab='experience'))

@edit_profile_bp.route('/updateexperience/<int:experience_id>', methods=['GET','POST'])
def update_experience(experience_id):
    form = request.form
    experience = Experience.query.get(experience_id)
    experience.organization_name = form.get('update-organization_name')
    experience.position = form.get('update-position')
    experience.start_date = form.get('update-start_date')
    experience.end_date = form.get('update-end_date')
    db.session.commit()
    flash('Experience updated Successfully','success')
    return redirect(url_for('profile.update_profile',tab='experience'))


@edit_profile_bp.route('/deleteexperience/<int:experience_id>', methods=['GET','POST'])
def delete_experience(experience_id):
    db.session.delete(Experience.query.get(experience_id))
    db.session.commit()
    flash('Experience deleted successfully','success')
    return redirect(url_for('profile.update_profile',tab='experience'))

@edit_profile_bp.route('/addeducation', methods=['GET','POST'])
def add_education():
    form = request.form
    new_education = Education(
        user_id = current_user.id,
        institution_name = form.get('add-institution_name'),
        course_name = form.get('add-course_name'),
        start_year = form.get('add-start_year'),
        end_year = form.get('add-end_year'),
    )

    db.session.add(new_education)
    db.session.commit()
    flash('Education added successfully','success')
    return redirect(url_for('profile.update_profile',tab='education'))

@edit_profile_bp.route('/updateeducation/<int:education_id>',methods=['GET','POST'])
def update_education(education_id):
    education = Education.query.get(education_id)
    form = request.form
    if education:
        education.institution_name = form.get('update-institution_name')
        education.course_name = form.get('update-course_name')
        education.start_year = form.get('update-start_year')
        education.end_year = form.get('update-end_year')
        db.session.commit()
        flash('Education updated successfully','success')
        return redirect(url_for('profile.update_profile'))
    
    flash('Education not found','error')
    return redirect(url_for('profile.update_profile',tab='education'))

@edit_profile_bp.route('/deleteeducation/<int:education_id>',methods=['GET','POST'])
def delete_education(education_id):
    education = Education.query.get(education_id)
    db.session.delete(education)
    db.session.commit()
    flash('Education deleted successfully','success')
    return redirect(url_for('profile.update_profile',tab='education'))