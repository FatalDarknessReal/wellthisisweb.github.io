from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, BooleanField
from wtforms.validators import DataRequired, Length


class RegistrationForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired(), Length(min=2, max=150)])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Зарегистрироваться')


class LoginForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')


class PasswordGenerationForm(FlaskForm):
    name = StringField('Имя сервиса', validators=[DataRequired()])
    length = IntegerField('Длина пароля', default=12)
    special_chars = BooleanField('Использовать специальные символы?')
    submit = SubmitField('Сгенерировать пароль')


class PasswordManagementForm(FlaskForm):
    password = StringField('Пароль', validators=[DataRequired()])
    update = SubmitField('Обновить пароль')
    delete = SubmitField('Удалить пароль')
