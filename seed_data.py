from app import app, db
from models import User, ObjetoPerdido
from werkzeug.security import generate_password_hash
from datetime import datetime

with app.app_context():
    # Crear admin si no existe
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(
            username='admin',
            password=generate_password_hash('admin123', method='pbkdf2:sha256'),
            role='admin'
        )
        db.session.add(admin)

    # Crear usuario de prueba
    user = User.query.filter_by(username='u12345678').first()
    if not user:
        user = User(
            username='u12345678',
            password=generate_password_hash('testpass', method='pbkdf2:sha256'),
            role='user'
        )
        db.session.add(user)
        db.session.commit()

    # Crear objetos perdidos/encontrados de ejemplo
    objetos = [
        ObjetoPerdido(
            nombre='iPhone 13 Pro',
            descripcion='iPhone color azul con case transparente. Se perdió en la cafetería durante el almuerzo.',
            area='Cafetería',
            fecha_encuentro=datetime.strptime('2025-05-28', '%Y-%m-%d'),
            nombre_persona='Ana García',
            contacto='ana.garcia@example.com',
            foto='iphone13.jpeg',  # asegúrate de tener esta imagen en static/uploads o usa un placeholder
            estado='Perdido',
            user_id=user.id
        ),
        ObjetoPerdido(
            nombre='Mochila Negra',
            descripcion='Mochila con libros y laptop. Encontrada en el pasillo del edificio B.',
            area='Pasillo',
            fecha_encuentro=datetime.strptime('2025-05-25', '%Y-%m-%d'),
            nombre_persona='Carlos Pérez',
            contacto='carlos.perez@example.com',
            foto='mochila_negra.jpeg',
            estado='Encontrado',
            user_id=user.id
        ),
    ]

    for obj in objetos:
        # Evitar duplicados si ya existen
        existe = ObjetoPerdido.query.filter_by(nombre=obj.nombre, area=obj.area).first()
        if not existe:
            db.session.add(obj)

    db.session.commit()
    print("Datos de ejemplo insertados correctamente.")
