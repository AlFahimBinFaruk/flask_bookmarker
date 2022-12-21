from flask import Flask,redirect,jsonify
from flask_jwt_extended import JWTManager
from .database import db,Bookmark
from .auth import auth
from .bookmarks import bookmarks
import os
from .constants.http_status_code import HTTP_404_NOT_FOUND,HTTP_500_INTERNAL_SERVER_ERROR

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
    
    # default route
    @app.get("/<short_url>")
    def index(short_url):
        bookmark = Bookmark.query.filter_by(short_url=short_url).first_or_404()  

        if bookmark:
            bookmark.visits = bookmark.visits + 1
            db.session.commit()
            return redirect(bookmark.url)
    
    # handle error routes
    @app.errorhandler(HTTP_404_NOT_FOUND)
    def handle404(e):
        return jsonify({
            "msg":"page not found"
        }),HTTP_404_NOT_FOUND
        
    @app.errorhandler(HTTP_500_INTERNAL_SERVER_ERROR)
    def handle500(e):
        return jsonify({
            "msg":"server error."
        }),HTTP_500_INTERNAL_SERVER_ERROR    


    return app    

# function to create a new sqlite db if already one not exits.
def create_db(app):
    if not os.path.exists("instance/test.db"):
        app.app_context().push()
        db.create_all()
        print("New DB Created.")    