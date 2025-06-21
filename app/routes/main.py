from flask import Blueprint, flash, request, redirect, url_for, render_template
from flask_login import login_required, login_user, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app.forms import LoginForm, RegistrationForm
from app.models import User
from app.extensions import db


main = Blueprint('main',__name__)

@main.route('/')
def home():
    return render_template('home/home.html', current_user=current_user)

@main.app_errorhandler(404)
def page_not_found(error):
    return render_template('error/404.html'), 404

@main.app_errorhandler(403)
def access_denied(error):
    return render_template('error/403.html'), 403


@main.app_errorhandler(401)
def access_denied(error):
    return render_template('error/401.html'), 401

@main.app_errorhandler(500)
def access_denied(error):
    return render_template('error/500.html'), 500