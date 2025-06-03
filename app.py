import os
from flask import Flask, render_template, redirect, url_for, flash, request, abort
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime
from models import db, User, ObjetoPerdido
from forms import LoginForm, RegisterForm, ReportObjectForm
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

# Permitir solo extensiones para subir fotos
ALLOWED_EXTENSIONS = app.config['ALLOWED_EXTENSIONS']

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.before_first_request
def create_tables():
    db.create_all()
    # Crear un admin por defecto si no existe
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin_user = User(
            username='admin',
            password=generate_password_hash('admin123', method='sha256'),
            role='admin'
        )
        db.session.add(admin_user)
        db.session.commit()

@app.route('/')
@login_required
def home():
    if current_user.role == 'admin':
        return redirect(url_for('admin_dashboard'))
    else:
        return redirect(url_for('user_dashboard'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            flash('Has iniciado sesión correctamente', 'success')
            return redirect(url_for('home'))
        else:
            flash('Usuario o contraseña incorrectos', 'danger')
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Has cerrado sesión', 'info')
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(username=form.username.data).first()
        if existing_user:
            flash('El usuario ya existe.', 'danger')
            return render_template('register.html', form=form)
        hashed_password = generate_password_hash(form.password.data, method='sha256')
        new_user = User(
            username=form.username.data,
            password=hashed_password,
            role='user'
        )
        db.session.add(new_user)
        db.session.commit()
        flash('Usuario registrado exitosamente. Ahora puedes iniciar sesión.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/user_dashboard')
@login_required
def user_dashboard():
    if current_user.role != 'user':
        abort(403)
    objetos = ObjetoPerdido.query.filter_by(user_id=current_user.id).all()
    return render_template('home.html', objetos=objetos)

@app.route('/report_object', methods=['GET', 'POST'])
@login_required
def report_object():
    if current_user.role != 'user':
        abort(403)
    form = ReportObjectForm()
    if form.validate_on_submit():
        file = form.foto.data
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
            filename = f"{current_user.username}_{timestamp}_{filename}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            file.save(filepath)
            
            nuevo_objeto = ObjetoPerdido(
                nombre=form.nombre.data,
                descripcion=form.descripcion.data,
                area=form.area.data,
                fecha_encuentro=datetime.strptime(form.fecha_encuentro.data, '%Y-%m-%d'),
                nombre_persona=form.nombre_persona.data,
                contacto=form.contacto.data,
                foto=filename,
                user_id=current_user.id
            )
            db.session.add(nuevo_objeto)
            db.session.commit()
            flash('Objeto reportado exitosamente', 'success')
            return redirect(url_for('user_dashboard'))
        else:
            flash('Formato de archivo no permitido', 'danger')
    return render_template('report_object.html', form=form)

@app.route('/admin_dashboard')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        abort(403)
    objetos = ObjetoPerdido.query.all()
    usuarios = User.query.filter(User.role == 'user').all()
    return render_template('admin_dashboard.html', objetos=objetos, usuarios=usuarios)

if __name__ == '__main__':
    app.run(debug=True)
