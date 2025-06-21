from flask_wtf import FlaskForm, RecaptchaField
from wtforms import Form, StringField, SelectField, PasswordField, SubmitField, HiddenField, TextAreaField, DateField, IntegerField
from wtforms.validators import InputRequired, EqualTo, Length, Email, ValidationError, URL, Optional
from .models import User
import re
from flask_wtf.file import FileField, FileAllowed


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[Email(), InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])
    recaptcha = RecaptchaField()
    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min=4, max=25)])
    email = StringField('Email', validators=[InputRequired(), Email()])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=6, max=20)])
    confirm_password = PasswordField('Confirm Password', validators=[InputRequired(), EqualTo('password','passwords do not match')])
    role = SelectField('Role',choices=[('student','Student'),('recruiter','Recruiter')], validators=[InputRequired()])
    recaptcha = RecaptchaField()
    submit = SubmitField('Register')

    def validate_email(self,email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already exists')
    
    def validate_password(self,password):
        pattern = r'^(?=.*[\d\W]).{6,}$'
        if not re.match(pattern, password.data):
            raise ValidationError('Password must be at least 6 characters long and contain at least one number or special character.')
        

class AdminForm(Form):
    user_id = HiddenField('User ID')
    username = StringField('Username', validators=[InputRequired()])
    email = StringField('Email', validators=[InputRequired(),Email()])
    role = SelectField('Role',choices=[('student','Student'),('recruiter','Recruiter'),('admin','Admin')])
    update = SubmitField('Update')
    delete = SubmitField('Delete')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[InputRequired(), Length(min=6, max=20)])
    confirm_password = PasswordField('Confirm Password', validators=[InputRequired(), EqualTo('password','passwords do not match')])
    submit = SubmitField('Reset Password')

class EmailForResetPasswordForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(),Email()])
    submit = SubmitField('Submit')

class ProfileForm(FlaskForm):
    photo = FileField('Profile Photo', validators=[FileAllowed(['jpg','jpeg','png'],'Only images files are allowed')])
    one_liner = StringField('Bio',validators=[Length(max=100)])
    bio = TextAreaField('Bio',validators=[Length(max=170)])
    college = StringField('College', validators=[Length(max=100)])
    education = TextAreaField('Education',validators=[Length(max=500)])
    linkedin_url = StringField('Linkedin URL', validators=[URL(), Optional()])
    github_url = StringField('Github URL', validators=[URL(), Optional()])
    resume = FileField('Resume', validators=[FileAllowed(['pdf'],'Only pdf files are allowed')])
    submit_profile = SubmitField('Update Profile')

class SkillsForm(FlaskForm):
    skills = StringField('Skills', validators=[InputRequired()])
    submit_skills = SubmitField('Update Skills')

class LanguagesForm(FlaskForm):
    languages = StringField('Languages', validators=[InputRequired()])
    submit_languages = SubmitField('Update Languages')

class ProjectForm(FlaskForm):
    title = StringField('Project Title', validators=[InputRequired(), Length(max=120)])
    description = StringField('Project Description', validators=[Optional()])
    link = StringField('Project URL (optional)', validators=[Optional(), URL()])
    submit_project = SubmitField('Update Project')

class ExperienceForm(FlaskForm):
    organization_name = StringField('Organization Name', validators=[InputRequired(), Length(max=120)])
    position = StringField('Position', validators=[InputRequired(), Length(max=50)])
    # description = StringField('Role Description', validators=[Optional()])
    start_date = DateField('Start Date', validators=[InputRequired()])
    end_date = DateField('End Date', validators=[Optional()])
    submit_experience = SubmitField('Update Experience')

class EducationForm(FlaskForm):
    institution_name = StringField('Institution Name', validators=[InputRequired()])
    course_name = StringField('Course Name', validators=[InputRequired()])
    start_year = IntegerField('Start Year',validators=[InputRequired(), Length(min=4,max=4)])
    end_year = IntegerField('End Year', validators=[Optional(),Length(min=4,max=4)])
    submit_education = SubmitField('Update Education')

class ChatBot(FlaskForm):
    input = StringField('Input', validators=[Optional()], render_kw={"placeholder": "type your message..."})
    submit_input = SubmitField('Send')