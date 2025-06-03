import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = 'tu_clave_secreta_muy_segura'  # Cambia esta clave para producción
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'database.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # Máximo 16 MB para archivos subidos
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
