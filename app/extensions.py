from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
import google.generativeai as genai
from config import GEMINI_API_KEY
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address



db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
mail = Mail()
limiter = Limiter(
    get_remote_address,
    default_limits=["200 per day","50 per hour"]
)

genai.configure(api_key=GEMINI_API_KEY)
gemini = genai.GenerativeModel("gemini-2.0-flash")



