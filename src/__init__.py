from flask import Flask
from flask_jwt_extended import JWTManager
from .database import db
from .auth import auth
from .bookmarks import bookmarks
import os

def create_app(test_config=None):
    app = Flask(__name__,instance_relative_config=True)

    if test_config is None:
        # Set app configuratins
        app.config.from_mapping(
            SECRET_KEY = os.environ.get("SECRET_KEY"),
            SQLALCHEMY_DATABASE_URI=os.environ.get("SQLALCHEMY_DATABASE_URI"),
            JWT_SECRET_KEY=os.environ.get("JWT_SECRET_KEY")
        )

    else:
        app.config.from_mapping(test_config)    
    
    # initialize db
    db.app = app
    db.init_app(app)
    create_db(app)

    # initialize jwt manager
    JWTManager(app)

    # register blueprints
    app.register_blueprint(auth)
    app.register_blueprint(bookmarks)    

    @app.get("/")
    def index():
        return "hi there."    

    return app    

# function to create a new sqlite db if already one not exits.
def create_db(app):
    if not os.path.exists("instance/test.db"):
        app.app_context().push()
        db.create_all()
        print("New DB Created.")    