from flask import Blueprint, flash, redirect, url_for, render_template, request
from app.models import User
from app.extensions import db
from flask_login import current_user
from utils.decorators import role_required
from app.forms import AdminForm
from werkzeug.security import generate_password_hash
import os
import subprocess
import sys

admin_bp = Blueprint('admin',__name__)

@admin_bp.route('/admin',methods=['GET','POST'])
@role_required(['admin'])
def edit_user():
    users = User.query.all()
    user_forms = [(user, AdminForm(obj=user)) for user in users]
    if request.method == 'POST':
        form = AdminForm(request.form)
        user = User.query.get(form.user_id.data)

        if form.delete.data:
            db.session.delete(user)
            db.session.commit()
            flash(f'user {form.user_id.data} deleted')
        elif form.update.data:
            user.username = form.username.data
            user.email = form.email.data
            user.role = form.role.data
            db.session.commit()
            flash(f'user {form.user_id.data} updated successfully')
        
        return redirect(url_for('admin.edit_user'))

    return render_template('admin/admin.html',user_forms=user_forms)


@admin_bp.route('/pushadmin')
def push_admin():
    user = User.query.filter_by(username='admin').first()
    if not user:
        new_admin = User(
            username = 'admin',
            email = 'svishaal67@gmail.com',
            password = generate_password_hash('vishaal#123'),
            role = 'admin',
            verified = True
        )
        db.session.add(new_admin)
        db.session.commit()
    return " "




@admin_bp.route('/admin/rebuild-vectors')
@role_required(['admin'])
def rebuild_vectors():
    project_root = os.path.abspath(os.path.dirname(__file__))  # /path/to/app
    root_dir = os.path.abspath(os.path.join(project_root, '..', '..'))  # two levels up
    script_path = os.path.join(root_dir, "build_vector_db_runner.py")

    try:
        subprocess.run([sys.executable, script_path], check=True)
        flash("Vector database rebuilt successfully.", "success")
    except subprocess.CalledProcessError as e:
        flash(f"Error rebuilding vector DB: {e}", "danger")

    return redirect(url_for('admin.edit_user'))


