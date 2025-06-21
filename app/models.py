from .extensions import db
from flask_login import UserMixin
from sqlalchemy import event
from sqlalchemy.orm import Session

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(120),unique=True, nullable=False)
    password = db.Column(db.String(512), nullable=False)
    role = db.Column(db.String(30), default='student')
    verified = db.Column(db.Boolean, default=False) 

    profile = db.relationship('Profile', backref='user', uselist=False, cascade='all, delete')
    skills = db.relationship('UserSkills', backref='user', cascade='all, delete')
    education = db.relationship('Education', backref='user', cascade='all, delete')
    languages = db.relationship('UserLanguages', backref='user', cascade='all, delete')
    projects = db.relationship('Projects', backref='user', cascade='all, delete')
    experiences = db.relationship('Experience', backref='user', cascade='all, delete')
    endorsements_received = db.relationship('Endorsement',foreign_keys='Endorsement.user_id', backref='endorsed_user', cascade='all, delete')
    endorsements_given = db.relationship('Endorsement',foreign_keys='Endorsement.endorsed_by', backref='endorser', cascade='all, delete')

class Profile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)
    one_liner = db.Column(db.Text)
    bio = db.Column(db.Text)
    photo = db.Column(db.String(255), default='default.jpg')
    college = db.Column(db.String(255), default='None') 
    linkedin_url = db.Column(db.String(255))
    github_url = db.Column(db.String(255))
    resume = db.Column(db.String(255), default='default.pdf')

class Education(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    institution_name = db.Column(db.String(512), nullable=False)
    course_name = db.Column(db.String(512), nullable=False)
    start_year = db.Column(db.String(10), nullable=False)
    end_year = db.Column(db.String(10), default='present')

class Skills(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    skill = db.Column(db.String(30))

    users = db.relationship('UserSkills', backref='skill', cascade='all, delete')
    endorsements = db.relationship('Endorsement', backref='skill', cascade='all, delete')

class UserSkills(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    skill_id = db.Column(db.Integer, db.ForeignKey('skills.id'), nullable=False)

    __table_args__ = (db.UniqueConstraint('user_id', 'skill_id', name='user_skill_id'),)


class Languages(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    language = db.Column(db.String(30), nullable=False)

    users = db.relationship('UserLanguages', backref='language', cascade='all, delete')

class UserLanguages(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    language_id = db.Column(db.Integer, db.ForeignKey('languages.id'), nullable=False)

class Projects(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text(),default="no description available")
    link = db.Column(db.String(255), default='no link available')

class Experience(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    organization_name = db.Column(db.String(120), nullable=False)
    position = db.Column(db.String(120), nullable=False)
    # description = db.Column(db.Text)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)

class Endorsement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    endorsed_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    skill_id = db.Column(db.Integer, db.ForeignKey('skills.id'), nullable=False)

    __table_args__ = (db.UniqueConstraint('user_id','endorsed_by','skill_id',name='unique_endorsement'),)



@event.listens_for(UserSkills, 'before_delete')
def delete_related_endorsements(mapper, connection, target):
    session = Session.object_session(target)

    session.query(Endorsement).filter_by(
        user_id=target.user_id,
        skill_id=target.skill_id
    ).delete(synchronize_session=False)
