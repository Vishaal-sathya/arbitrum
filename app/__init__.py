from flask import Flask
from .extensions import db, migrate, login_manager, mail, limiter
from .models import User
from config import Config


def create_app():
    app = Flask(__name__)

    app.config.from_object(Config)
    db.init_app(app)
    migrate.init_app(app,db)
    mail.init_app(app)
    limiter.init_app(app)


    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    @login_manager.user_loader
    def user_loader(user_id):
        return User.query.get(user_id)

    from .routes.auth import auth
    app.register_blueprint(auth)

    from .routes.main import main
    app.register_blueprint(main)

    from .routes.admin import admin_bp
    app.register_blueprint(admin_bp)

    from .routes.edit_profile import edit_profile_bp
    app.register_blueprint(edit_profile_bp)

    from .routes.view_profile import view_profile_bp
    app.register_blueprint(view_profile_bp)

    from .routes.search import search_bp
    app.register_blueprint(search_bp)

    from .routes.chatbot import chatbot_bp
    app.register_blueprint(chatbot_bp)
    
    return app