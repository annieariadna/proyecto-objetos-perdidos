from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, FileField, SelectField
from wtforms.validators import DataRequired, Length, Regexp, EqualTo, ValidationError
from flask_wtf.file import FileAllowed, FileRequired

class LoginForm(FlaskForm):
    username = StringField('Usuario', validators=[
        DataRequired(),
        Regexp(r'^u\d{8}$', message="El usuario debe empezar con 'u' seguido de 8 números")
    ])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    submit = SubmitField('Ingresar')

class RegisterForm(FlaskForm):
    username = StringField('Usuario', validators=[
        DataRequired(),
        Regexp(r'^u\d{8}$', message="El usuario debe empezar con 'u' seguido de 8 números")
    ])
    password = PasswordField('Contraseña', validators=[
        DataRequired(),
        Length(min=6),
        EqualTo('confirm', message='Las contraseñas deben coincidir')
    ])
    confirm = PasswordField('Confirmar Contraseña', validators=[DataRequired()])
    submit = SubmitField('Registrar')

class ReportObjectForm(FlaskForm):
    nombre = StringField('Nombre del objeto', validators=[DataRequired(), Length(max=100)])
    descripcion = TextAreaField('Descripción', validators=[Length(max=500)])
    area = StringField('Área donde se encontró', validators=[DataRequired(), Length(max=100)])
    fecha_encuentro = StringField('Fecha del hallazgo', validators=[DataRequired()])
    nombre_persona = StringField('Nombre de la persona que encontró', validators=[DataRequired(), Length(max=100)])
    contacto = StringField('Contacto', validators=[DataRequired(), Length(max=100)])
    foto = FileField('Foto del objeto', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Solo imágenes con extensión jpg, jpeg, png, gif'),
        FileRequired('Se requiere una foto del objeto')
    ])
    submit = SubmitField('Reportar Objeto')
