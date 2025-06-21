from itsdangerous import URLSafeTimedSerializer
from flask import current_app


EMAIL_VERFICATION_SALT = 'email-verification-salt'
PASSWORD_RESET_SALT = 'password-reset-salt'

def generate_email_token(email, salt):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return serializer.dumps(email, salt=salt)


def confirm_email_token(token, salt, expiration=3600):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        email = serializer.loads(token, salt=salt, max_age=expiration)
    except Exception:
        return None
    return email
