import os
import environ
from datetime import timedelta
from flask_jwt_extended import create_access_token, create_refresh_token, decode_token
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from flask_jwt_extended import verify_jwt_in_request, get_jwt
from flask import jsonify

def get_env() -> str:
    """This functions reads the environmental variables file and loads it
    to the script so the variables can be used.

    Args:
        No Args.

    Returns:
        [Env Object]: [Environmental object of the environ library with the environmental variables]
    """
    try:
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        env = environ.Env(DEBUG=(bool, False))
        environ.Env.read_env(os.path.join(BASE_DIR, '../config/.env'))
        return env
    except:
        raise ValueError("Revisa que el archivo de variables de entorno se llame .env y esté en la misma carpera que este script")
    
def create_token(identity, additional_claims=None):
    access_token = create_access_token(
        identity=str(identity),
        fresh=True,
        additional_claims=additional_claims or {},
        expires_delta=timedelta(minutes=15)
    )
    refresh_token = create_refresh_token(identity=identity)
    return {
        'access_token': access_token,
        'refresh_token': refresh_token
    }

def verify_token(token):
    try:
        return decode_token(token)
    except Exception as e:
        return None

def hash_password(password):
    return generate_password_hash(password)

def verify_password(hashed_password, password):
    return check_password_hash(hashed_password, password)

def get_jwt_config(env):
    return {
        'JWT_SECRET_KEY': env('JWT_SECRET_KEY'),
        'JWT_ACCESS_TOKEN_EXPIRES': timedelta(minutes=15),
        'JWT_REFRESH_TOKEN_EXPIRES': timedelta(days=30),
        'JWT_TOKEN_LOCATION': ['headers', 'cookies'],
        'JWT_COOKIE_SECURE': env('ENVIRONMENT') == 'production',
        'JWT_COOKIE_CSRF_PROTECT': True
    }

def role_required(roles):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            if claims['role'] not in roles:
                return jsonify({"msg": "Acceso no autorizado"}), 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator