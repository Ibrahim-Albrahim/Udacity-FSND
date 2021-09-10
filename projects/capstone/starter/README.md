# capstone-gallery Project

## About
Photographer can create galleries and post photos related to a gallery. I developed this project to make use of the knowledge you acquired in this nanodegree and hence gain confidence in these skills.

## Getting Started

Authentication: This application requires authentication to perform various actions. All the endpoints require
various permissions, except the index endpoint, that are passed via the `Bearer` token.

The application has two different types of roles:
- Viewer
  - can only view the list of galleries and photos.
  - has `get:galleries , get:photos` permissions
- Photographer
  - can perform all the actions that `viewer` can
  - can also create a gallery and photo and also update respective information
  - has `get:galleries , get:photos , delete:galleries , delete:photos , patch:galleries , post:galleries , post:photos` permissions.

### Installing Dependencies

#### Python 3.7

Follow instructions to install the latest version of python for your platform in the [python docs](https://docs.python.org/3/using/unix.html#getting-and-installing-the-latest-version-of-python)

#### Virtual Environment (venv)
We recommend working within a virtual environment whenever using Python for
projects. This keeps your dependencies for each project separate and organaized.
Instructions for setting up a virual enviornment for your platform can be found
in the python docs.

python3 -m venv venv
venv/bin/activate

#### PIP Dependencies

In the capstone-gallery directory, run the following to install all necessary dependencies:

```bash
pip3 install -r requirements.txt
```

This will install all of the required packages.

##### Key Dependencies

- [Flask](http://flask.pocoo.org/)  is a lightweight backend microservices framework. Flask is required to handle requests and responses.

- [SQLAlchemy](https://www.sqlalchemy.org/) is the Python SQL toolkit and ORM we'll use handle the lightweight sqlite database. You'll primarily work in app.py and can reference models.py. 

- [Flask-CORS](https://flask-cors.readthedocs.io/en/latest/#) is the extension we'll use to handle cross origin requests from our frontend server. 

## Running the server
Once you create the database, open your terminal, navigate to the root folder, and run:

flask db init
flask db migrate
flask db upgrade
After running, don't forget modify 'SQLALCHEMY_DATABASE_URI' variable.

## Local Testing
To test your local installation, run the following command from the root folder:

## python -m test_app.py
If all tests pass, your local installation is set up correctly.

## Running the server
From within the root directory, first ensure you're working with your created
venv. To run the server, execute the following:

export FLASK_APP=app.py
export FLASK_DEBUG=true
export FLASK_ENV=development
flask run
Setting the FLASK_ENV variable to development will detect file changes and
restart the server automatically.
We can now also open the application via Heroku using the URL:
https://capstone-gallery.herokuapp.com/

The live application can only be used to generate tokens via Auth0, the endpoints have to be tested using curl or Postman 
using the token since I did not build a frontend for the application.

## DATA MODELING:
#### models.py
The schema for the database and helper methods to simplify API behavior are in models.py:
- There are three tables created: Gallery, and Photo
- The Gallery table has a foreign key on the photo table for gallery_id.
- Gallery and Photo tables are used by the role 'Photographer' to add new galleries and photos, and to retrieve these galleries.

## API ARCHITECTURE AND TESTING
### Endpoint Library

@app.errorhandler decorators were used to format error responses as JSON objects. Custom @requires_auth decorator were used for Authorization based
on roles of the viewer. Two roles are assigned to this API: 'photographer' and 'viewer'. The 'viewer' role is assigned by default when someone creates an account
from the login page, while the 'viewer' role is already pre-assigned to certain viewers.

A token needs to be passed to each endpoint. 
The following only works for /products endpoints:
The token can be retrived by following these steps:
1. Go to https: http://localhost:5000/login and enter any credentials into the Auth0 login page. The role is automatically assigned by Auth0. 
2. Enter any credentials into the Auth0 login page. The role is automatically assigned by Auth0. 
   Alternatively, sample account that has already been created can be used:
   Email: photographer@capstone-gallery.com
   Password: !Abc1234


#### GET '/'
Returns a list of all available photos belonging to the gallery, and a success value.
Sample curl: 
curl -i -H "Content-Type: application/json" -H "Authorization: Bearer {INSERT_TOKEN_HERE}" http://localhost:5000/
Sample response output:
[
   {
      "id":1,
      "title":"gallery 1"
   }
   {
      "id":2,
      "title":"gallery 2"
   }
]

#### GET '/1'
Returns a list of all available photos belonging to the gallery, and a success value.
Sample curl: 
curl -i -H "Content-Type: application/json" -H "Authorization: Bearer {INSERT_TOKEN_HERE}" http://localhost:5000/1 
Sample response output:
[
    {
        "id": 2,
        "photo_title": "photo 2"
    },
    {
        "id": 4,
        "photo_title": "photo 1"
    }
]


#### POST '/gallery/create'
Returns a list of all products belonging to gallery, along with new product posted, a success value, and total number of products.
Sample curl: 
curl http://localhost:5000/gallery/create -X POST -H "Content-Type: application/json" -H "Authorization: Bearer {INSERT_TOKEN_HERE}" -d '{"title":"gallery 1"}'
Sample response output:
[
   {
      "id":1,
      "title":"gallery 1"
   }
]


#### PATCH '/{gallery_id}/edit'
Returns a list of all products belonging to gallery, along with updated product, a success value, and total number of products.
Sample curl:
curl http://localhost:5000/1/edit -X POST -H "Content-Type: application/json" -H "Authorization: Bearer {INSERT_TOKEN_HERE}" -d '{"title":"gallery 2"}'
Sample response output:
[
   {
      "id":1,
      "title":"gallery 2"
   }
]


#### DELETE '/gallery/{gallery_id}/delete'
Returns a list of all products after deleting the requested product, a success value, and total number of products.
curl http://localhost:5000/gallery/1/delete -X DELETE -H "Content-Type: application/json" -H "Authorization: Bearer {INSERT_TOKEN_HERE}" 
Sample response output:
{
   "success": True
}

#### POST '/photo/create'
Returns a list of all products belonging to gallery, along with new product posted, a success value, and total number of products.
Sample curl: 
curl http://localhost:5000/photo/create -X POST -H "Content-Type: application/json" -H "Authorization: Bearer {INSERT_TOKEN_HERE}" -d '{"title": "photo 2","gallery_id": 2}'
Sample response output:
   {
      "success": true
   }


#### DELETE '/photo/{photo_id}/delete'
Returns a list of all products after deleting the requested product, a success value, and total number of products.
curl http://localhost:5000/photo/1/delete -X DELETE -H "Content-Type: application/json" -H "Authorization: Bearer {INSERT_TOKEN_HERE}" 
Sample response output:
{
   "success": True
}

To get the tokens for endpoints, we need the payload to contain the photograpgher role permissions.
For this, we can once again go to the hosted heroku URL:
1. Go to https: https://capstone-gallery.herokuapp.com/login
2. Enter the following credentials into Auth0, which has been designated with Photographer role:
   Email: photographer@capstone-gallery.com
   Password: !Abc1234

## Testing
There are 5 unittests in test_app.py. To run this file use:
```
DROPDB gallerytwo
CREATEDB gallerytwo
python test_app.py
```
the file 'capstone-project-gallery.postman_collection.json' contains postman tests containing tokens for specific roles.
To run this file, follow the steps:
1. Go to postman application.
2. Load the collection --> Import -> directory/capstone-project-gallery.postman_collection.json
3. Click on the runner, select the collection and run all the tests.

## THIRD-PARTY AUTHENTICATION
#### auth.py
Auth0 is set up and running. The following configurations are in a .env file which is exported by the app:
- The Auth0 Domain Name
- The JWT code signing secret
- The Auth0 Client ID
The JWT token contains the permissions for the 'Photographer' and 'viewer' roles.

## DEPLOYMENT
The app is hosted live on heroku at the URL: 
https://capstone-gallery.herokuapp.com/

However, there is no frontend for this app yet, and it can only be presently used to authenticate using Auth0 by entering
credentials and retrieving a fresh token to use with curl or postman.
