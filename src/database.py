from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import random
import string

db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True) # user tablosnun id sütunu olarak tanımlanıyor primary key olarak
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.Text(), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, default=datetime.now())
    bookmarks = db.relationship('Bookmark', backref='user')
    def __repr__(self):
        return '<User %r>' % self.username

class Bookmark(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.Text, nullable=False)
    short_url = db.Column(db.String(3), nullable=False)
    body = db.Column(db.Text, nullable=False)
    visits = db.Column(db.Integer, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) # user tablosunun id sütunu ile bağlantı kuruluyor
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, default=datetime.now())

    def generate_short_characters(self):
        characters =  string.digits + string.ascii_letters
        picked_characters ="".join(random.choices(characters, k=3))
        link = self.query.filter_by(short_url=picked_characters).first()

        if link:
            return self.generate_short_characters()
        else:
            return picked_characters

    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.short_url = self.generate_short_characters()


    def __repr__(self):
        return '<Bookmark %r>' % self.url