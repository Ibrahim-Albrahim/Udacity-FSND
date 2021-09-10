from re import T
from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, ForeignKey
from sqlalchemy.orm import relationship
import os
import os
import re


# DB_PATH = 'postgresql://postgres:1234@localhost:5432/gallery'
uri = os.getenv("DATABASE_URL")  # or other relevant config var
if uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)
# uri = os.environ['DATABASE_URL']
app = Flask(__name__)


db = SQLAlchemy()

'''
setup_db(app)
    binds a flask application and a SQLAlchemy service
'''
def setup_db(app, uri=uri):
# def setup_db(app):
    # app.config["SQLALCHEMY_DATABASE_URI"] = 'postgresql://postgres:1234@localhost:5432/gallery'
    app.config["SQLALCHEMY_DATABASE_URI"] = uri
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    Migrate(app, db)
    db.init_app(app)
    db.create_all()
    
    

class inheritedClassName(db.Model):
    __abstract__ = True
    def insert(self):
        db.session.add(self)
        db.session.commit()
    def delete(self):
        db.session.delete(self)
        db.session.commit()
    def update(self):
        db.session.commit()

class Gallery(inheritedClassName):
    __tablename__ = 'Gallery'
    id = db.Column(db.Integer,  primary_key=True)
    title = db.Column(db.String(128), nullable=False)
    photos = relationship("Photo", back_populates="gallery")
    def __repr__(self):
        return f'Gallery Id: {self.id} Gallery Name: {self.title}'


class Photo(inheritedClassName):
    __tablename__ = 'Photo'
    id = db.Column(db.Integer,  primary_key=True)
    title = db.Column(db.String(128), nullable=False)
    gallery_id = db.Column(Integer, ForeignKey('Gallery.id'))
    gallery = relationship("Gallery", back_populates="photos")
    def __repr__(self):
        return f'Photo Id: {self.id} Gallery: {self.gallery} Photo Name: {self.title}'


