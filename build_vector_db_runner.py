

from app import create_app
from app.extensions import db
from vector_builder import build_vector_db  

app = create_app()

with app.app_context():
    build_vector_db()
