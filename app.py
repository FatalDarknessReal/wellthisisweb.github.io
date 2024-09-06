from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from models import db, User, Password  # Импортируйте db, User и Password из models.py
from forms import RegistrationForm, LoginForm  # Убедитесь, что вы импортируете формы
from forms import PasswordGenerationForm
import os
import random
import string

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///passwords.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Инициализация SQLAlchemy и других расширений
db.init_app(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))  # Использование метода get() сессии


# Генерация пароля
def generate_password(length=12, use_special_chars=True):
    characters = string.ascii_letters + string.digits
    if use_special_chars:
        characters += string.punctuation
    return ''.join(random.choice(characters) for _ in range(length))


@app.route('/')
def home():
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            flash('Вы успешно вошли в систему!', 'success')
            return redirect(url_for('main_menu'))  # Перенаправление на главную страницу
        flash('Неверное имя пользователя или пароль', 'danger')
    return render_template('login.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        username = form.username.data
        password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        flash('Регистрация успешна! Теперь вы можете войти.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)


@app.route('/main_menu')
@login_required
def main_menu():
    passwords = Password.query.filter_by(user_id=current_user.id).all()  # Получаем все пароли пользователя
    return render_template('main_menu.html', passwords=passwords)


@app.route('/generate', methods=['GET', 'POST'])
@login_required
def generate():
    form = PasswordGenerationForm()  # Создание экземпляра формы
    if form.validate_on_submit():
        password_length = form.length.data
        use_special_chars = form.special_chars.data
        password = generate_password(password_length, use_special_chars)

        new_password = Password(user_id=current_user.id, name=form.name.data, password=password)
        db.session.add(new_password)
        db.session.commit()
        flash('Пароль сгенерирован и сохранен!', 'success')
        return redirect(url_for('main_menu'))  # Перенаправление на главное меню
    return render_template('generate.html', form=form)  # Передача формы в шаблон


@app.route('/manage/<int:password_id>', methods=['GET', 'POST'])
@login_required
def manage_password(password_id):
    print(f"Запрос на управление паролем с ID: {password_id}")  # Отладочное сообщение
    password_entry = Password.query.get_or_404(password_id)  # Получаем пароль по ID
    if password_entry.user_id != current_user.id:
        flash('Нет доступа к этому паролю!', 'danger')
        return redirect(url_for('main_menu'))

    if request.method == 'POST':
        if 'update' in request.form:
            password_entry.password = request.form['password']
            db.session.commit()
            flash('Пароль обновлен!', 'success')
        elif 'delete' in request.form:
            db.session.delete(password_entry)
            db.session.commit()
            flash('Пароль удален!', 'success')
        return redirect(url_for('main_menu'))  # Перенаправление на главное меню

    return render_template('manage_password.html', password=password_entry)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Создание всех таблиц
    app.run(debug=True)