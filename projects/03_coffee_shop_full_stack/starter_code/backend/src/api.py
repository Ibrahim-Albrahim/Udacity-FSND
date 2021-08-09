import os
from flask import (Flask,
                request,
                abort,
                jsonify,)
from sqlalchemy import exc
import json
from flask_cors import CORS
# from werkzeug.exceptions import HTTPException
from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
db_drop_and_create_all()

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks')
def get_drinks():
    drinks = list(map(Drink.short,Drink.query.all()))
    result = {"success": True, "drinks": drinks}
    return jsonify(result)

'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drinks_detail():
    drinks = list(map(Drink.long,Drink.query.all()))
    result = {"success": True, "drinks": drinks}
    return jsonify(result)

'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks', method=['POST'])
@requires_auth('post:drinks')
def post_drinks():
    drinks_data = request.get_json()
    try:
        drink = Drink(
            title=drinks_data['titile'],
            recipe=drinks_data['recipe'])
        Drink.insert(drink)

        drinks = list(map(Drink.long,Drink.query.all()))
        result = {"success": True, "drinks": drinks}
        return jsonify(result)

    except:
        abort(500)




'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks/<id>', method=['PATCH'])
@requires_auth('patch:drinks')
def patch_drinks(token, drink_id):
    new_drink_data = request.get_json()
    old_drink_data = Drink.query.get(drink_id)
    if old_drink_data is None:
        abort(404)

    if 'title' in new_drink_data:
        setattr(old_drink_data, 'title', new_drink_data['title'])
    if 'recipe' in new_drink_data:
        setattr(old_drink_data, 'recipe', new_drink_data['recipe'])

    try:
        Drink.update(old_drink_data)
        drinks = list(map(Drink.long,Drink.query.all()))
        result = {"success": True, "drinks": drinks}
        return jsonify(result)

    except:
        abort(500)

'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks/<id>', method=['DELETE'])
@requires_auth('delete:drinks')
def delete_drinks(token,drink_id):
    drink = Drink.query.get(drink_id)
    if drink is None:
        abort(404)
    
    try:
        Drink.delete(drink)

        drinks = list(map(Drink.long,Drink.query.all()))
        result = {"success": True, "drinks": drinks}
        return jsonify(result)

    except:
        abort(500)


# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''
@app.errorhandler(404)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404

'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''
@app.errorhandler(Exception)
def handle_error(e):
    code = 404
    # if isinstance(e, HTTPException):
    if isinstance(e):
        code = e.code
    return jsonify(error=str(e)), code

'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''
@app.errorhandler(AuthError)
def auth_error(e):
    return jsonify(e.error), e.status_code