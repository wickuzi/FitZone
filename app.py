from flask import Flask, render_template, request, redirect, url_for, flash,session
from config import config
from flask_mysqldb import MySQL
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import LoginManager, login_user, logout_user, login_required
from flask_wtf import CSRFProtect

app = Flask(__name__)

ROLES = {
    'cajero': 'cajero123',
    'mantenimiento': 'mantenimiento123'
}
@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods =['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        rol = request.form.get('rol')
        password = request.form.get('password')

        if not rol or not password:
            flash('Todos los campos deben ser rellenados!')
            return redirect(url_for('login'))
        
        if password != ROLES[rol]:
            flash('Contraseña de módulo incorrecta!')
            return redirect(url_for('login'))
        
        if rol in ROLES and password == ROLES[rol]:
            session['rol'] = rol
            if rol == 'cajero':
                return redirect(url_for('cajero'))
            elif rol == 'mantenimiento':
                return redirect(url_for('mantenimiento'))
            else:
                flash('Contraseña de modulo incorrecta')
                return redirect(url_for('login'))

    return render_template('auth/login.html', error=error)

@app.route('/cajero')
def cajero():
    if 'rol' not in session or session['rol'] != 'cajero':
        return redirect(url_for('login'))
    return render_template('auth/cajero.html')

@app.route('/mantenimiento')
def mantenimiento():
    if 'rol' not in session or session['rol'] != 'mantenimiento':
        return redirect(url_for('login'))
    return render_template('auth/mantenimiento.html')  

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.config.from_object(config['development'])
    app.run()