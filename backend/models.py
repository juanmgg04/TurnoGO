from flask_sqlalchemy import SQLAlchemy
import datetime
import enum

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=True)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Integer, db.ForeignKey('roles.id'))
    created_at = db.Column(db.DateTime, default=datetime.datetime.now())

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'role': self.role,
            'created_at': self.created_at
        }
    
    def __str__(self) -> str:
        return self.id
    
class Role(db.Model):
    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now())

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'created_at': self.created_at
        }
    
    def __str__(self) -> str:
        return self.id
    
# class Permissions(db.Model):
#     __tablename__ = 'permissions'

#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(255), nullable=False)
    
#     def serialize(self):
#         return {
#             'id': self.id,
#             'name':self.name
#         }
    
#     def __str__(self) -> str:
#         return self.id
    
# class RolePermissions(db.Model):
#     __tablename__ = 'role_permissions'

#     id = db.Column(db.Integer, primary_key=True)
#     role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
#     permission_id = db.Column(db.Integer, db.ForeignKey('permissions.id'))
    
#     def serialize(self):
#         return {
#             'id': self.id,
#             'role_id': self.role_id,
#             'permission_id': self.permission_id
#         }
    
#     def __str__(self) -> str:
#         return self.id
    
class services(db.Model):
    __tablename__ = 'services'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now())

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'created_at': self.created_at
        }
    
    def __str__(self) -> str:
        return self.id
    
class Status(enum.Enum):
    pending = 'pending'
    confirmed = 'confirmed'
    canceled = 'canceled'
    
class appointments(db.Model):
    __tablename__ = 'appointments'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    service_id = db.Column(db.Integer, db.ForeignKey('services.id'))
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False) 
    status = db.Column(db.Enum(Status), default=Status.pending, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now())

    def serialize(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'service_id': self.service_id,
            'date': self.date,
            'time': self.time,
            'status': self.status,
            'created_at': self.created_at
        }

    def __str__(self) -> str:
        return self.id


                                                     