from flask_migrate import Migrate
from app.extensions import db
from app.models import User, Profile,Education, Skills, UserSkills, Languages, UserLanguages, Projects, Experience, Endorsement
from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)