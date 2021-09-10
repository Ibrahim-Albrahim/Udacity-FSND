import os
from flask import (
    Flask,
    request,
    abort,
    jsonify,)
from flask_cors import CORS
from werkzeug.exceptions import HTTPException
from werkzeug.utils import redirect
from models import Photo,Gallery, setup_db, db
from auth import AuthError, requires_auth
from authlib.integrations.flask_client import OAuth
from os import environ as env
import constants
from dotenv import load_dotenv, find_dotenv
import sys


def create_app(test_config=None):
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
    setup_db(app)
    app.secret_key = os.urandom(32)
    CORS(app, resources={r"/*": {"origins": "*"}})

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET, POST, PATCH, DELETE, OPTIONS')
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
    link = 'https://'
    link += AUTH0_DOMAIN
    link += '/authorize?'
    link += 'audience=' + AUTH0_AUDIENCE + '&'
    link += 'response_type=token&'
    link += 'client_id=' + AUTH0_CLIENT_ID + '&'
    link += 'redirect_uri=' + AUTH0_CALLBACK_URL

    @app.route('/login')
    def login():
        return redirect(link)

    @app.route('/', methods=['GET'])
    def index():
        galleries=Gallery.query.all()
        data = []
        for gallery in galleries:
            data.append ({
                'id': gallery.id,
                'title': gallery.title
            })
        return jsonify(data)

    @app.route('/<gallery_id>' , methods=['GET'])
    @requires_auth('get:photos')
    def show_gallery(gallery_id):
        gallery = Gallery.query.get(gallery_id)
        data = []
        for photo in gallery.photos:
            gallery = Gallery.query.get(photo.gallery_id)
            data.append ({
                'id': photo.id,
                'photo_title': photo.title,
            })

        return jsonify(data)
        

    @app.route('/gallery/create', methods=['POST'])
    @requires_auth('post:galleries')
    def create_gallery():
        request_data = request.get_json()
        try:
                newGallery = Gallery(title = request_data["title"])
                db.session.add(newGallery)
                db.session.commit() 
                result = {"success": True}
                return jsonify(result)
        except ImportError:
                db.session.rollback()
                result = {"success": False}
                return jsonify(result)
                print(sys.exc_info())

        finally:
            db.session.close() 

    @app.route('/<gallery_id>/edit', methods=['PATCH','POST'])
    @requires_auth('patch:galleries')
    def edit_gallery_submission(gallery_id):
        request_data = request.get_json()
        gallery = Gallery.query.get(gallery_id)
        gallery.title = request_data["title"]
        
        try:
            db.session.commit()
            result = {"success": True}
        except ImportError:
            db.session.rollback()
            result = {"success": False}
            print(sys.exc_info())
        finally:
            db.session.close()
            return jsonify(result)

    @app.route('/gallery/<gallery_id>/delete', methods=['DELETE','GET'])
    @requires_auth('delete:galleries')
    def delete_gallery(gallery_id):
        gallery = Gallery.query.get(gallery_id)
        try:
            db.session.delete(gallery)
            db.session.commit()
            result = {"success": True}
            return jsonify(result)

        except ImportError:
            error_on_delete = True
            db.session.rollback()
        finally:
            db.session.close()
        if error_on_delete:
            print(sys.exc_info())
            abort(500)

    @app.route('/photo/create', methods=['POST'])
    @requires_auth('post:photos')
    def create_photo():
        request_data = request.get_json()
        try:
                newPhoto = Photo(title = request_data["title"], gallery_id = request_data["gallery_id"])
                db.session.add(newPhoto)
                db.session.commit() 
                result = {"success": True}
                return jsonify(result)
        except ImportError:
                db.session.rollback()
                result = {"success": False}
                print(sys.exc_info())
                return jsonify(result)
        finally:
            db.session.close() 


    @app.route('/photo/<photo_id>/delete', methods=['DELETE','GET'])
    @requires_auth('delete:photos')
    def delete_photo(photo_id):
        photo = Photo.query.get(photo_id)
        try:
            db.session.delete(photo)
            db.session.commit()
        except ImportError:
            error_on_delete = True
            db.session.rollback()
        finally:
            db.session.close()
        if error_on_delete:
            print(sys.exc_info())
            abort(500)
        else:
            result = {"success": True}
            return jsonify(result)




    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "unprocessable"
        }), 422

    @app.errorhandler(404)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "resource not found"
        }), 404


    @app.errorhandler(Exception)
    def handle_error(e):
        code = 404
        if isinstance(e, HTTPException):
        # if isinstance(e):
            code = e.code
        return jsonify(error=str(e)), code


    @app.errorhandler(AuthError)
    def auth_error(e):
        return jsonify(e.error), e.status_code


    return app

app = create_app()

if __name__ == '__main__':
    app.run()