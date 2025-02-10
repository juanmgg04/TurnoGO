from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
import models
from utils import *
from flask_migrate import Migrate
import os
# from twilio.rest import Client  
import datetime

env = get_env()
app = Flask(__name__)

# Configuración
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

# # Configuración Twilio (WhatsApp)
# twilio_client = Client(env('TWILIO_ACCOUNT_SID'), env('TWILIO_AUTH_TOKEN'))
# WHATSAPP_FROM = env('TWILIO_WHATSAPP_NUMBER')

class AuthController:
    @app.route('/login', methods=['POST'])
    def login():
        data = request.get_json()
        user = models.User.query.filter_by(email=data.get('email')).first()
        
        if user and verify_password(user.password, data.get('password')):
            role = models.Role.query.get(user.role)
            tokens = create_token(identity=user.id, additional_claims={
                'role': user.role,
                'email': user.email
            })
            return jsonify({
                "msg": "Login exitoso",
                "tokens": tokens,
                "user": {
                    "id": user.id,
                    "name": user.name,
                    "role": role.name
                }
            }), 200
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
            role=2  # Rol de usuario por defecto
        )
        models.db.session.add(new_user)
        models.db.session.commit()
        return jsonify({"msg": "Usuario registrado", "user": new_user.serialize()}), 201

    @app.route('/forgot-password', methods=['POST'])
    def forgot_password():
        email = request.json.get('email')
        user = models.User.query.filter_by(email=email).first()
        if not user:
            return jsonify({"msg": "Si el email existe, se enviarán instrucciones"}), 200
        
        reset_token = create_access_token(
            identity=user.id,
            expires_delta=timedelta(minutes=15),
            additional_claims={'password_reset': True}
        )
        # Enviar token por WhatsApp/Email (Implementar lógica de envío real)
        print(f"Token de recuperación: {reset_token}")  # Solo para desarrollo
        return jsonify({"msg": "Instrucciones enviadas"}), 200

    @app.route('/reset-password', methods=['POST'])
    @jwt_required()
    def reset_password():
        claims = get_jwt()
        if not claims.get('password_reset'):
            return jsonify({"msg": "Token inválido"}), 401
            
        user_id = get_jwt_identity()
        new_password = hash_password(request.json.get('new_password'))
        
        user = models.User.query.get(user_id)
        user.password = new_password
        models.db.session.commit()
        
        return jsonify({"msg": "Contraseña actualizada"}), 200

class AppointmentController:
    @app.route('/appointments', methods=['POST'])
    @jwt_required()
    @role_required([2])  # Solo usuarios
    def create_appointment():
        user_id = get_jwt_identity()
        data = request.get_json()
        
        new_appointment = models.appointments(
            user_id=user_id,
            service_id=data['service_id'],
            date=datetime.datetime.strptime(data['date'], '%Y-%m-%d').date(),
            time=datetime.datetime.strptime(data['time'], '%H:%M').time(),
            status=models.Status.pending
        )
        models.db.session.add(new_appointment)
        models.db.session.commit()
        
        # self._send_whatsapp_confirmation(new_appointment)
        return jsonify(new_appointment.serialize()), 201

    @app.route('/appointments', methods=['GET'])
    @jwt_required()
    def get_appointments():
        user_id = get_jwt_identity()
        user = models.User.query.get(user_id)
        
        if user.role == 1:  # Admin
            appointments = models.appointments.query.all()
        else:
            appointments = models.appointments.query.filter_by(user_id=user_id)
            
        return jsonify([a.serialize() for a in appointments]), 200

    @app.route('/appointments/<int:appointment_id>', methods=['DELETE'])
    @jwt_required()
    def delete_appointment(appointment_id):
        appointment = models.appointments.query.get(appointment_id)
        current_user = get_jwt_identity()
        
        if not appointment:
            return jsonify({"msg": "Cita no encontrada"}), 404
        
        if appointment.user_id != current_user and models.User.query.get(current_user).role != 1:
            return jsonify({"msg": "No autorizado"}), 403
            
        models.db.session.delete(appointment)
        models.db.session.commit()
        # self._send_whatsapp_cancellation(appointment)
        return jsonify({"msg": "Cita eliminada"}), 200

    def _send_whatsapp_confirmation(self, appointment):
        try:
            user = models.User.query.get(appointment.user_id)
            service = models.services.query.get(appointment.service_id)
            message = (f"Confirmación de cita\n"
                      f"Servicio: {service.name}\n"
                      f"Fecha: {appointment.date} {appointment.time}")
            
            # twilio_client.messages.create(
            #     body=message,
            #     from_=WHATSAPP_FROM,
            #     to=f'whatsapp:{user.phone}'  # Necesitarías agregar campo phone al usuario
            # )
        except Exception as e:
            print(f"Error enviando WhatsApp: {e}")

class AdminController:
    @app.route('/admin/appointments/<int:appointment_id>', methods=['PUT'])
    @jwt_required()
    @role_required([1])
    def update_appointment(appointment_id):
        appointment = models.appointments.query.get(appointment_id)
        data = request.get_json()
        
        if 'status' in data:
            appointment.status = models.Status[data['status']]
        if 'date' in data:
            appointment.date = datetime.datetime.strptime(data['date'], '%Y-%m-%d').date()
        if 'time' in data:
            appointment.time = datetime.datetime.strptime(data['time'], '%H:%M').time()
        
        models.db.session.commit()
        # self._send_whatsapp_update(appointment)
        return jsonify(appointment.serialize()), 200

    @app.route('/admin/services', methods=['POST'])
    @jwt_required()
    @role_required([1])
    def create_service():
        data = request.get_json()
        new_service = models.services(
            name=data['name'],
            description=data['description'],
            price=data['price']
        )
        models.db.session.add(new_service)
        models.db.session.commit()
        return jsonify(new_service.serialize()), 201

    @app.route('/admin/users', methods=['GET'])
    @jwt_required()
    @role_required([1])
    def get_users():
        users = models.User.query.all()
        return jsonify([u.serialize() for u in users]), 200
    
    @app.route('/admin/Register', methods=['POST'])
    @jwt_required()
    @role_required([1])
    def register_admin():
        data = request.get_json()
        if models.User.query.filter_by(email=data['email']).first():
            return jsonify({"msg": "El usuario ya existe"}), 400
            
        hashed_pw = hash_password(data['password'])
        new_user = models.User(
            name=data['name'],
            email=data['email'],
            password=hashed_pw,
            role=1  # Rol de admin por defecto
        )
        models.db.session.add(new_user)
        models.db.session.commit()
        return jsonify({"msg": "Usuario registrado", "user": new_user.serialize()}), 201
    
    @app.route('/admin/delete/<int:user_id>', methods=['DELETE'])
    @jwt_required()
    @role_required([1])
    def delete_user(user_id):
        user = models.User.query.get(user_id)
        if not user:
            return jsonify({"msg": "Usuario no encontrado"}), 404
        
        models.db.session.delete(user)
        models.db.session.commit()
        return jsonify({"msg": "Usuario eliminado"}), 200
class ServiceController:
    @app.route('/services', methods=['GET'])
    def get_services():
        services = models.services.query.all()
        return jsonify([s.serialize() for s in services]), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)