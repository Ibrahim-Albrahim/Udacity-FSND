import os
from flask import Flask, render_template, request, Response, flash, redirect, url_for, abort, jsonify
from flask_cors import CORS
from models import Photo,Gallery, setup_db, db
from flask_moment import Moment
from werkzeug.utils import secure_filename

from base64 import b64encode
import base64
from io import BytesIO #Converts data from Database into bytes



app = Flask(__name__)
moment = Moment(app)

setup_db(app)
app.secret_key = os.urandom(32)
CORS(app)

def render_picture(data):

    render_pic = base64.b64encode(data).decode('ascii') 
    return render_pic


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html', galleries=Gallery.query.all())

@app.route('/galleries/<gallery_id>' , methods=['GET'])
def show_gallery(gallery_id):
#   gallery = Gallery.query(Gallery).get(gallery_id)
#   photos = Photo.query(Photo).get(gallery_id)
  photos = db.session.query(Photo.id, Photo.rendered_data).join(Gallery,Gallery.photo_id==Photo.id).filter(Gallery.photo_id==Photo.id).all()
  data = []

  for photo in photos:
    data.append({
      "photo_id": photo.id,
      "photo_rendered_data": photo.rendered_data
    })

  return render_template('gallery.html',photosdata=data)
    
@app.route('/add-gallery')
def addGallery():
  return render_template('add-gallery.html')


@app.route('/gallery/create', methods=['POST'])
def create_gallery():
   file = request.files['inputFile']
   data = file.read()
   render_file = render_picture(data)
   title = request.form['title']

   newFile = Photo(name=file.filename, data=data, rendered_data=render_file, title=title)
   try:
    db.session.add(newFile)
    db.session.commit() 
   except:
    db.session.rollback()
    flash(f'An error occurred creating gallery {title}.')
   finally:
       db.session.close() 


   return redirect(url_for('index')) 
        


@app.route('/gallery/<gallery_id>/delete', methods=['DELETE'])
def delete_gallery(gallery_id):
    gallery = Gallery.query.get(gallery_id)
    if not gallery:
        return redirect(url_for('index'))
    else:
        error_on_delete = False
        gallery_title = gallery.title
        try:
            db.session.delete(gallery)
            db.session.commit()
        except:
            error_on_delete = True
            db.session.rollback()
        finally:
            db.session.close()
        if error_on_delete:
            flash(f'An error occurred deleting gallery {gallery_title}.')
            print("Error in delete_gallery()")
            abort(500)
        else:
            return jsonify({
                'deleted': True,
                'url': url_for('gallery')
            })


@app.route('/photos', methods=['GET'])
def photos():
    data = []
    photos = Photo.query.all()
    
    for photo in photos:
        data.append({
            "photo_id": photo.id,
            "photo_title": photo.title,
            "gallery_thum": photo.thum,
        })

    return render_template('photos.html', photos=data)

@app.route('/add-photo')
def addPhoto():
  return render_template('add-photo.html')

@app.route('/photo/create', methods=['POST'])
def create_photo():
   file = request.files['inputFile']
   data = file.read()
   render_file = render_picture(data)
   gallery = request.form['gallery']

   newFile = Photo(name=file.filename, data=data, rendered_data=render_file, gallery=gallery)

   try:
    db.session.add(newFile)
    db.session.commit() 
    flash(f'photo added successfully.')

   except:
    db.session.rollback()
    flash(f'An error occurred adding photo.')
   finally:
       db.session.close() 


   return redirect(url_for('index')) 


@app.route('/photo/<photo_id>/delete', methods=['GET'])
def delete_photo(photo_id):
    photo = Photo.query.get(photo_id)
    if not photo:
        return redirect(url_for('index'))
    else:
        error_on_delete = False
        photo_title = photo.title
        try:
            db.session.delete(photo)
            db.session.commit()
        except:
            error_on_delete = True
            db.session.rollback()
        finally:
            db.session.close()
        if error_on_delete:
            flash(f'An error occurred deleting venue {photo_title}.')
            print("Error in delete_gallery()")
            abort(500)
        else:
            return jsonify({
                'deleted': True,
                'url': url_for('photo')
            })



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)