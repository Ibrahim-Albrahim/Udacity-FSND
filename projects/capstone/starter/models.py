from flask import Flask
from flask_moment import Moment
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime



DB_PATH = 'postgresql://postgres:1234@localhost:5432/gallery'
app = Flask(__name__)


db = SQLAlchemy()

'''
setup_db(app)
    binds a flask application and a SQLAlchemy service
'''
def setup_db(app):
    app.config["SQLALCHEMY_DATABASE_URI"] = DB_PATH
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    Migrate(app, db)
    db.init_app(app)
    db.create_all()


class Gallery(db.Model):
    __tablename__ = 'Gallery'
    id = db.Column(db.Integer,  primary_key=True)
    title = db.Column(db.String(128), nullable=False)
    name = db.Column(db.String(128), nullable=False)
    data = db.Column(db.LargeBinary, nullable=False) #Actual data, needed for Download
    rendered_data = db.Column(db.Text, nullable=False)#Data to render the pic in browser
    photo_id = db.Column(db.Integer, db.ForeignKey('Photo.id'), nullable=True)

    def __repr__(self):
        return f'Gallery Id: {self.id} Gallery Name: {self.title} Thumnail: {self.rendered_data}'



class Photo(db.Model):
    __tablename__ = 'Photo'
    id = db.Column(db.Integer,  primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    data = db.Column(db.LargeBinary, nullable=False) #Actual data, needed for Download
    rendered_data = db.Column(db.Text, nullable=False)#Data to render the pic in browser
    gallery = db.relationship('Gallery', backref='photo', lazy=True)

    def __repr__(self):
        return f'Photo Id: {self.id} Pic Name: {self.name} Photo: {self.rendered_data} Gallery: {self.gallery}'

