import os
from flask import Flask, render_template, redirect, url_for, flash, request, abort, jsonify
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_mail import Mail, Message
from datetime import datetime
from models import db, User, ObjetoPerdido
from forms import LoginForm, RegisterForm, ReportObjectForm
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

# Configuración de correo para Gmail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # Servidor SMTP de Google
app.config['MAIL_PORT'] = 465  # Usa SSL (puedes usar 587 si prefieres TLS)
app.config['MAIL_USE_TLS'] = False  # Usar TLS, en este caso no es necesario ya que usamos SSL
app.config['MAIL_USE_SSL'] = True  # Usar SSL
app.config['MAIL_USERNAME'] = 'tu_correo@gmail.com'  # Tu correo de Gmail
app.config['MAIL_PASSWORD'] = 'tu_contraseña'  # Tu contraseña de Gmail o contraseña de aplicación
app.config['MAIL_DEFAULT_SENDER'] = 'tu_correo@gmail.com'  # El correo que aparecerá como remitente

# Inicialización de Flask-Mail
mail = Mail(app)

login_manager = LoginManager()
login_manager.login_view = 'login'  # Especifica la ruta para login
login_manager.init_app(app)

# Redirige sin mostrar el mensaje "Please log in to access this page"
@login_manager.unauthorized_handler
def unauthorized():
    return redirect(url_for('login'))  # Redirige sin el mensaje predeterminado

ALLOWED_EXTENSIONS = app.config['ALLOWED_EXTENSIONS']

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.before_request
def create_tables_once():
    if not hasattr(app, 'tables_created'):
        db.create_all()
        app.tables_created = True
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin_user = User(
                username='admin',
                password=generate_password_hash('admin123', method='pbkdf2:sha256'),
                role='admin'
            )
            db.session.add(admin_user)
            db.session.commit()

@app.route('/')
@login_required
def home():
    return redirect(url_for('inicio'))

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
        hashed_password = generate_password_hash(form.password.data, method='pbkdf2:sha256')
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

@app.route('/marcar_encontrado/<int:objeto_id>', methods=['POST'])
@login_required
def marcar_encontrado(objeto_id):
    if current_user.role != 'admin':
        abort(403)
    
    objeto = ObjetoPerdido.query.get_or_404(objeto_id)
    objeto.estado = 'Encontrado'
    db.session.commit()
    
    return jsonify({'message': 'Objeto marcado como encontrado'})

@app.route('/eliminar_objeto/<int:objeto_id>', methods=['POST'])
@login_required
def eliminar_objeto(objeto_id):
    if current_user.role != 'admin':
        abort(403)
    
    objeto = ObjetoPerdido.query.get_or_404(objeto_id)
    db.session.delete(objeto)
    db.session.commit()
    
    flash('Reporte de objeto eliminado correctamente.', 'success')
    return redirect(url_for('admin_dashboard'))


@app.route('/admin_dashboard')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        abort(403)
    
    objetos = ObjetoPerdido.query.all()  # Mostrar todos los objetos
    usuarios = User.query.filter(User.role == 'user').all()  # Obtener todos los usuarios
    return render_template('admin_dashboard.html', objetos=objetos, usuarios=usuarios)

@app.route('/inicio')
@login_required
def inicio():
    query = ObjetoPerdido.query

    # Filtros por query params
    desc = request.args.get('descripcion', '', type=str)
    ubicacion = request.args.get('ubicacion', '', type=str)
    estado = request.args.get('estado', '', type=str)
    fecha = request.args.get('fecha', '', type=str)

    if desc:
        query = query.filter(
            db.or_(
                ObjetoPerdido.nombre.ilike(f'%{desc}%'),
                ObjetoPerdido.descripcion.ilike(f'%{desc}%')
            )
        )
    if ubicacion:
        query = query.filter(ObjetoPerdido.area == ubicacion)
    if estado:
        query = query.filter(ObjetoPerdido.estado == estado)
    if fecha:
        try:
            fecha_dt = datetime.strptime(fecha, '%Y-%m-%d')
            query = query.filter(db.func.date(ObjetoPerdido.fecha_encuentro) == fecha_dt.date())
        except ValueError:
            pass

    objetos = query.order_by(ObjetoPerdido.fecha_encuentro.desc()).all()
    areas = ['Cafetería', 'Cancha', 'Pasillo', 'Piso', 'Salón', 'Laboratorio']
    return render_template('inicio.html', objetos=objetos, areas=areas)

@app.route('/enviar_contacto', methods=['POST'])
@login_required
def enviar_contacto():
    data = request.get_json()
    contactoEmail = data.get('contactoEmail')  # Correo del usuario que ha reportado el objeto
    mensaje = data.get('mensaje')

    msg = Message('Nuevo mensaje de contacto', recipients=[contactoEmail])
    msg.body = f"Mensaje: {mensaje}"
    
    try:
        mail.send(msg)
        return jsonify({'message': 'Mensaje enviado exitosamente'}), 200
    except Exception as e:
        print(f"Error al enviar mensaje: {e}")
        return jsonify({'message': 'Error al enviar mensaje'}), 500
    
@app.route('/manage_users')
@login_required
def manage_users():
    if current_user.role != 'admin':
        abort(403)  # Solo los administradores pueden acceder
    usuarios = User.query.all()  # Muestra todos los usuarios
    return render_template('manage_users.html', usuarios=usuarios)

@app.route('/statistics')
@login_required
def statistics():
    if current_user.role != 'admin':
        abort(403)  # Solo los administradores pueden acceder a las estadísticas
    # Lógica para mostrar estadísticas
    return render_template('statistics.html')  # Reemplaza con tu plantilla de estadísticas

@app.route('/perfil')
@login_required
def perfil():
    return render_template('perfil.html')  # Asegúrate de tener esta plantilla
   
@app.route('/report/<int:reporte_id>')
@login_required
def view_report(reporte_id):
    objeto = ObjetoPerdido.query.get_or_404(reporte_id)
    return render_template('view_report.html', obj=objeto)


if __name__ == '__main__':
    app.run(debug=True)

# Restante del código...
