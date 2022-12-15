from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import string
import random

db = SQLAlchemy()


# bookmark model
class Bookmark(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    body = db.Column(db.Text,nullable=True)
    url = db.Column(db.Text,nullable=False)
    short_url = db.Column(db.String(3),nullable=True)
    visits = db.Column(db.Integer,default=0)
    user_id = db.Column(db.Integer,db.ForeignKey("user.id"))
    created_at = db.Column(db.DateTime,default=datetime.utcnow)
    updated_at = db.Column(db.DateTime,onupdate=datetime.utcnow)

    # genereate a new short_url every time a new book mark is added
    def genarate_short_url(self):
        chars = string.digits+string.ascii_letters
        picked_chars = "".join(random.choices(chars,k=3))

        link = self.query.filter_by(short_url=picked_chars).first()

        if link:
            self.genarate_short_url()
        else:
            return picked_chars

    def __init__(self,**args) -> None:
        super().__init__(**args)
         
        # set the short_url 
        self.short_url = self.genarate_short_url()            


# user model
class User(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(150),nullable=False)
    email = db.Column(db.String(150),nullable=False,unique=True)
    password = db.Column(db.Text,nullable=False)
    created_at = db.Column(db.DateTime,default=datetime.utcnow)
    updated_at = db.Column(db.DateTime,onupdate=datetime.utcnow)
    bookmarks = db.relationship("Bookmark",backref="user")

