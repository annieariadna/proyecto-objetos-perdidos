from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(9), unique=True, nullable=False)  # Ejemplo: u22209220
    password = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(10), nullable=False, default='user')  # 'admin' o 'user'
    
    objetos = db.relationship('ObjetoPerdido', backref='reporter', lazy=True)

class ObjetoPerdido(db.Model):
    __tablename__ = 'objetos_perdidos'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text, nullable=True)
    area = db.Column(db.String(100), nullable=False)
    fecha_encuentro = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    nombre_persona = db.Column(db.String(100), nullable=False)
    contacto = db.Column(db.String(100), nullable=False)
    foto = db.Column(db.String(150), nullable=True) 
    estado = db.Column(db.String(20), nullable=False, default='Perdido')
 # Nombre del archivo de la foto
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
