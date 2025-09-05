from app import create_app, db
import sqlalchemy as sa
import sqlalchemy.orm as so
from app.models import User, Post

flask_app = create_app()

@flask_app.shell_context_processor
def make_shell_context():
    return {'sa':sa, 'so': so,'db': db, 'User': User,'Post': Post}