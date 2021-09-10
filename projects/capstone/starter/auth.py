import json
from flask import request
from functools import wraps
from jose import jwt
from urllib.request import urlopen
from os import environ as env
import constants
from dotenv import load_dotenv, find_dotenv

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

AUTH0_CALLBACK_URL = env.get(constants.AUTH0_CALLBACK_URL)
AUTH0_CLIENT_ID = env.get(constants.AUTH0_CLIENT_ID)
AUTH0_CLIENT_SECRET = env.get(constants.AUTH0_CLIENT_SECRET)
AUTH0_DOMAIN = env.get(constants.AUTH0_DOMAIN)
AUTH0_BASE_URL = 'https://' + AUTH0_DOMAIN
API_AUDIENCE = env.get(constants.AUTH0_AUDIENCE)
ALGORITHMS = env.get(constants.ALGORITHMS)

class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


def get_token_auth_header():
    if "Authorization" in request.headers:
        auth_header = request.headers["Authorization"]
        if auth_header:
            bearer_token_array = auth_header.split(' ')
            if bearer_token_array[0] and bearer_token_array[0].lower() == "bearer" and bearer_token_array[1]:
                return bearer_token_array[1]
    raise AuthError({
        'success': False,
        'message': 'JWT not found',
        'error':    1
    }, 401)


def check_permissions(permission, payload):
    if "permissions" in payload:
        if permission in payload['permissions']:
            return True
    raise AuthError({
        'success': False,
        'message': 'Permission not found in JWT',
        'error': 403
    }, 403)


def verify_decode_jwt(token):
    jsonurl = urlopen(f'http://{AUTH0_DOMAIN}/.well-known/jwks.json')
    jwks = json.loads(jsonurl.read())

    unverified_header = jwt.get_unverified_header(token)

    rsa_key = {}
    if 'kid' not in unverified_header:
        raise AuthError({
            'success': False,
            'message': 'Authorization malformed',
            'error': 401,
        }, 401)

    for key in jwks['keys']:
        if key['kid'] == unverified_header['kid']:
            rsa_key = {
                'kty': key['kty'],
                'kid': key['kid'],
                'use': key['use'],
                'n': key['n'],
                'e': key['e']
            }

    if rsa_key:
        try:
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=ALGORITHMS,
                audience=API_AUDIENCE,
                issuer='https://' + AUTH0_DOMAIN + '/'
            )

            return payload

        except jwt.ExpiredSignatureError:
            raise AuthError({
                'success': False,
                'message': 'Token expired',
                'error': 401,
            }, 401)

        except jwt.JWTClaimsError:
            raise AuthError({
                'success': False,
                'message': 'Incorrect claims. Please, check the audience and issuer',
                'error': 401,
            }, 401)
        except Exception:
            raise AuthError({
                'success': False,
                'message': 'Unable to parse authentication token',
                'error': 400,
            }, 400)
    raise AuthError({
        'success': False,
        'message': 'Unable to find the appropriate key',
        'error': 400,
    }, 400)


def requires_auth(permission=''):
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = get_token_auth_header()
            payload = verify_decode_jwt(token)
            check_permissions(permission, payload)
            return f(*args, **kwargs)

        return wrapper
    return requires_auth_decorator
