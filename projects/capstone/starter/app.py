import os
from flask import (Flask,
                render_template,
                request,
                flash,
                redirect,
                url_for,
                abort,
                jsonify)
from flask_cors import CORS
from models import Photo,Gallery, setup_db, db
from flask_moment import Moment
from auth.auth import AuthError, requires_auth
import base64



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

@app.route('/<gallery_id>' , methods=['GET'])
@requires_auth('get:photos')
def show_gallery(gallery_id):
  gallery = Gallery.query.get(gallery_id)
  data = []
  for photo in gallery.photos:
    gallery = Gallery.query.get(photo.gallery_id)
    data.append ({
        'id': photo.id,
        'rendered_data': photo.rendered_data,
    })

  return render_template('gallery.html',photosdata=data)
    
@app.route('/add-gallery')
def addGallery():
  return render_template('add-gallery.html')


@app.route('/gallery/create', methods=['POST'])
@requires_auth('post:galleries')
def create_gallery():
   file = request.files['inputFile']
   data = file.read()
   render_file = render_picture(data)
   title = request.form['title']

   newFile = Gallery(name=file.filename, data=data, rendered_data=render_file, title=title)
   try:
    db.session.add(newFile)
    db.session.commit() 
   except:
    db.session.rollback()
    flash(f'An error occurred creating gallery {title}.')
   finally:
       db.session.close() 


   return redirect(url_for('index')) 
        
@app.route('/<gallery_id>/edit', methods=['PATCH','GET'])
@requires_auth('patch:galleries')
def edit_gallery(gallery_id):
    gallery = Gallery.query.get(gallery_id)
    return render_template('edit-gallery.html', gallery=gallery)


@app.route('/<gallery_id>/edit', methods=['PATCH','POST'])
@requires_auth('patch:galleries')
def edit_gallery_submission(gallery_id):
    gallery = Gallery.query.get(gallery_id)
    gallery.title = request.form['title']
    
    if not gallery:
        return redirect(url_for('index'))
    else:
        error_on_delete = False
        gallery_title = gallery.title
        try:
            db.session.commit()
        except:
            error_on_delete = True
            db.session.rollback()
        finally:
            db.session.close()
        if error_on_delete:
            flash(f'An error occurred editing gallery {gallery_title}.')
            print("Error in edit_gallery()")
            abort(500)
        else:
            return redirect(url_for('index')) 

@app.route('/gallery/<gallery_id>/delete', methods=['DELETE','GET'])
@requires_auth('delete:galleries')
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


@app.route('/add-photo')
@requires_auth('post:photos')
def addPhoto():
  return render_template('add-photo.html')

@app.route('/photo/create', methods=['POST'])
@requires_auth('post:photos')
def create_photo():
   file = request.files['inputFile']
   data = file.read()
   render_file = render_picture(data)
   gallery_id = int(request.form['gallery'])

   newFile = Photo(name=file.filename, data=data, rendered_data=render_file, gallery_id=gallery_id)

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


@app.route('/photo/<photo_id>/delete', methods=['DELETE','GET'])
@requires_auth('delete:photos')
def delete_photo(photo_id):
    photo = Photo.query.get(photo_id)
    if not photo:
        return redirect(url_for('index'))
    else:
        error_on_delete = False
        try:
            db.session.delete(photo)
            db.session.commit()
        except:
            error_on_delete = True
            db.session.rollback()
        finally:
            db.session.close()
        if error_on_delete:
            flash(f'An error occurred deleting photo {photo_id}.')
            print("Error in delete_photo()")
            abort(500)
        else:
            return redirect(url_for('index')) 


@app.errorhandler(AuthError)
def auth_error(e):
    return jsonify(e.error), e.status_code


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)