from flask import Blueprint, flash, request, redirect, url_for, render_template
from flask_login import login_required, login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from app.forms import LoginForm, RegistrationForm, ResetPasswordForm, EmailForResetPasswordForm
from app.models import User
from app.extensions import db, limiter
from flask_mail import Message
from app.extensions import mail
from utils.tokens import generate_email_token, confirm_email_token, EMAIL_VERFICATION_SALT, PASSWORD_RESET_SALT



auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET','POST'])
@limiter.limit("10 per 5 minutes")
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password,form.password.data):
            if user.verified:
                login_user(user)
                flash('Login Successful')
                if user.profile is None:
                    return redirect(url_for('profile.update_profile'))
                
                return redirect(url_for('main.home'))
                    
            else:
                flash('Please verify mail before login')
        else:
            if not user:
                flash('Email does not exist')
            elif not check_password_hash(user.password,form.password.data):
                flash('Password is incorrect')
    return render_template('auth/login.html', form=form)


def send_verification_email(user):
    token = generate_email_token(user.email, EMAIL_VERFICATION_SALT)
    verify_url = url_for('auth.verify_email', token=token, _external=True)
    html = render_template('auth/verify_email.html', verify_url=verify_url)
    msg = Message('Verify your email', html=html, recipients=[user.email])
    mail.send(msg)


@auth.route('/register', methods=['GET','POST'])
@limiter.limit("5 per hour")
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        password = form.password.data
        hashed_password = generate_password_hash(password)
        new_user = User(
            username = form.username.data,
            email = form.email.data,
            password = hashed_password,
            role = form.role.data
        )
        db.session.add(new_user)
        db.session.commit()
        send_verification_email(new_user)
        return render_template('auth/verify_notice.html')
    return render_template('auth/register.html', form=form)

@auth.route('/verify/<token>')
def verify_email(token):
    email = confirm_email_token(token, EMAIL_VERFICATION_SALT)
    if not email:
        flash('The verification link as expired, please try again.','danger')
        return redirect(url_for('auth.register'))
    user = User.query.filter_by(email=email).first()
    if not user:
        flash('Account not found','danger')
        return redirect(url_for('auth.register'))
    if user.verified:
        flash('Account already verified')
    else:
        user.verified = True
        db.session.commit()
        flash('Account has been verified','success')
    
    return redirect(url_for('auth.login'))
    

@auth.route('/logout', methods=['GET','POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


def send_password_reset_mail(user):
    token = generate_email_token(user.email, PASSWORD_RESET_SALT)
    verification_url = url_for('auth.reset_password', token=token, _external=True)
    html = render_template('auth/reset_password_mail.html', url=verification_url)
    msg = Message('Click to reset password', html=html, recipients=[user.email])
    mail.send(msg)

@auth.route('/resetpassword', methods=['GET','POST'])
def reset_password_page():
    form = EmailForResetPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_mail(user)
            flash('Password reset email sent. Check your inbox.')
        else:
            flash('user not found')
    return render_template('auth/reset_password_page.html',form=form)

@auth.route('/resetpassword/<token>', methods=['GET','POST'])
def reset_password(token):
    email = confirm_email_token(token, PASSWORD_RESET_SALT)
    if email:
        user = User.query.filter_by(email=email).first()
        if user:
            form = ResetPasswordForm()
            if form.validate_on_submit():
                hashed_password = generate_password_hash(form.password.data)
                user.password = hashed_password
                db.session.commit()
                flash('password reset successfully')
                return redirect(url_for('auth.login'))
            return render_template('auth/password_reset_form.html', form=form)
        else:
            flash('user not found')
            return redirect(url_for('auth.login'))
    else:
        flash('token expired or invalid')
        return redirect(url_for('auth.login'))
