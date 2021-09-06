import os
from flask import (Flask,
                render_template,
                request,
                flash,
                redirect,
                url_for,
                session,
                abort,
                jsonify,
                _request_ctx_stack)
from flask_cors import CORS, cross_origin
from models import Photo,Gallery, setup_db, db
from flask_moment import Moment
from auth import AuthError, requires_auth
import base64
from authlib.integrations.flask_client import OAuth
from jose import jwt
from functools import wraps
import json
from urllib.request import urlopen
from dotenv import load_dotenv, find_dotenv
from os import environ as env
from werkzeug.exceptions import HTTPException
import constants

from six.moves.urllib.parse import urlencode


ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

AUTH0_CALLBACK_URL = env.get(constants.AUTH0_CALLBACK_URL)
AUTH0_CLIENT_ID = env.get(constants.AUTH0_CLIENT_ID)
AUTH0_CLIENT_SECRET = env.get(constants.AUTH0_CLIENT_SECRET)
AUTH0_DOMAIN = env.get(constants.AUTH0_DOMAIN)
AUTH0_BASE_URL = 'https://' + AUTH0_DOMAIN
AUTH0_AUDIENCE = env.get(constants.AUTH0_AUDIENCE)
    
app = Flask(__name__)
moment = Moment(app)

setup_db(app)
app.secret_key = os.urandom(32)
CORS(app)

@app.errorhandler(Exception)
def handle_auth_error(ex):
    response = jsonify(message=str(ex))
    response.status_code = (ex.code if isinstance(ex, HTTPException) else 500)
    return response

oauth = OAuth(app)

auth0 = oauth.register(
    'auth0',
    client_id=AUTH0_CLIENT_ID,
    client_secret=AUTH0_CLIENT_SECRET,
    api_base_url=AUTH0_BASE_URL,
    access_token_url=AUTH0_BASE_URL + '/oauth/token',
    authorize_url=AUTH0_BASE_URL + '/authorize',
    client_kwargs={
        'scope': 'openid profile email',
    },
)



def render_picture(data):

    render_pic = base64.b64encode(data).decode('ascii') 
    return render_pic

@app.route('/login')
def login():
    return auth0.authorize_redirect(redirect_uri=AUTH0_CALLBACK_URL, audience=AUTH0_AUDIENCE)

@app.route('/user')
@requires_auth
def dashboard():
    return render_template('dashboard.html',
                           userinfo=session['profile'],
                           userinfo_pretty=json.dumps(session['jwt_payload'], indent=4))

    
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
@requires_auth('post:galleries')
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




if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)