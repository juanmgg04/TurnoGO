from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
import models
from utils import get_env, get_jwt_config
from flask_migrate import Migrate
import os
from utils import *

env = get_env()
basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)

# Configuración de la base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{env("DB_DIRECTORY")}/{env("DB_NAME")}.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configuración JWT
jwt_config = get_jwt_config(env)
for key, value in jwt_config.items():
    app.config[key] = value

# Inicializar extensiones
models.db.init_app(app)
jwt = JWTManager(app)
migrate = Migrate(app, models.db)

# Rutas de autenticación
class Auth:
    @app.route('/login', methods=['POST'])
    def login():
        data = request.get_json()
        user = models.User.query.filter_by(email=data.get('email')).first()
        
        if user and verify_password(user.password, data.get('password')):
            tokens = create_token(identity=user.id, additional_claims={
                'role': user.role,
                'email': user.email
            })
            return jsonify(tokens), 200
        return jsonify({"msg": "Credenciales inválidas"}), 401

    @app.route('/register', methods=['POST'])
    def register():
        data = request.get_json()
        if models.User.query.filter_by(email=data['email']).first():
            return jsonify({"msg": "El usuario ya existe"}), 400
            
        hashed_pw = hash_password(data['password'])
        new_user = models.User(
            name=data['name'],
            email=data['email'],
            password=hashed_pw,
            role=1  # Asignar rol por defecto
        )
        models.db.session.add(new_user)
        models.db.session.commit()
        
        return jsonify(new_user.serialize()), 201

    # Ruta protegida de ejemplo
    @app.route('/profile', methods=['GET'])
    @jwt_required()
    def profile():
        current_user = get_jwt_identity()
        user = models.User.query.get(current_user)
        return jsonify(user.serialize())
    
    @app.route('/reset_password', methods=['POST'])
    @jwt_required()
    def reset_password():
        current_user = get_jwt_identity()
        user = models.User.query.get(current_user)
        data = request.get_json()
        if verify_password(user.password, data['old_password']):
            user.password = hash_password(data['new_password'])
            models.db.session.commit()
            return jsonify({"msg": "Contraseña actualizada"}), 200
        return jsonify({"msg": "Contraseña incorrecta"}), 401
    
class Role:
    @app.route('/roles', methods=['GET'])
    def get_roles():
        roles = models.Role.query.all()
        return jsonify([role.serialize() for role in roles])
    
    @app.route('/role', methods=['POST'])
    def create_role():
        data = request.get_json()
        new_role = models.Role(name=data['name'])
        models.db.session.add(new_role)
        models.db.session.commit()
        
        return jsonify(new_role.serialize()), 201
    
    @app.route('/role/<int:id>', methods=['PUT'])
    def update_role(id):
        data = request.get_json()
        role = models.Role.query.get(id)
        role.name = data['name']
        models.db.session.commit()
        
        return jsonify(role.serialize()), 200
    
    @app.route('/role/<int:id>', methods=['DELETE'])
    def delete_role(id):
        role = models.Role.query.get(id)
        models.db.session.delete(role)
        models.db.session.commit()
        
        return jsonify({"msg": "Rol eliminado"}), 200
    



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)