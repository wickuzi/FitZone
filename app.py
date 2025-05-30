import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
import psycopg2
from psycopg2.extras import RealDictCursor
from config import config

app = Flask(__name__)
app.config.from_object(config['development'])
bcrypt = Bcrypt(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login_gimnasio'

# Conexion
def get_db_connection():
    db_url = os.getenv('DATABASE_URL') or app.config['DATABASE_URL']
    conn = psycopg2.connect(db_url, cursor_factory=RealDictCursor)
    return conn

class Gimnasio(UserMixin):
    def __init__(self, id, nombre, contrasena):
        self.id = id
        self.nombre = nombre
        self.contrasena = contrasena

    def get_id(self):
        return str(self.id)

    @property
    def username(self):
        return self.nombre

@login_manager.user_loader
def load_user(user_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM gimnasios WHERE id = %s", (user_id,))
    gimnasio = cur.fetchone()
    cur.close()
    conn.close()
    if gimnasio:
        return Gimnasio(gimnasio['id'], gimnasio['nombre'], gimnasio['contrasena'])
    return None

@app.route('/')
def index():
    return redirect(url_for('introduction'))

@app.route('/introduction')
def introduction():
    return render_template('auth/intro.html')

@app.route('/registro_gimnasio', methods=['GET', 'POST'])
def registro_gimnasio():
    if request.method == 'POST':
        nombre = request.form['nombre']
        contrasena = request.form['contrasena']
        hashed = bcrypt.generate_password_hash(contrasena).decode('utf-8')

        conn = get_db_connection()
        cur = conn.cursor()
        try:
            cur.execute("INSERT INTO gimnasios (nombre, contrasena) VALUES (%s, %s)", (nombre, hashed))
            conn.commit()
            flash('Gimnasio registrado exitosamente.')
            return redirect(url_for('login_gimnasio'))
        except psycopg2.errors.UniqueViolation:
            conn.rollback()
            flash('Ese nombre de gimnasio ya existe.')
        finally:
            cur.close()
            conn.close()

    return render_template('auth/register.html')

@app.route('/login_gimnasio', methods=['GET', 'POST'])
def login_gimnasio():
    if request.method == 'POST':
        nombre = request.form['nombre']
        contrasena = request.form['contrasena']

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM gimnasios WHERE nombre = %s", (nombre,))
        gimnasio = cur.fetchone()
        cur.close()
        conn.close()

        if gimnasio and bcrypt.check_password_hash(gimnasio['contrasena'], contrasena):
            user = Gimnasio(gimnasio['id'], gimnasio['nombre'], gimnasio['contrasena'])
            login_user(user)
            return redirect(url_for('modulos'))
        else:
            flash('Nombre o contrase\u00f1a incorrectos.')

    return render_template('auth/login.html')

@app.route('/modulos')
@login_required
def modulos():
    return render_template('auth/modulos.html', username=current_user.username)

@app.route('/cajero', methods=['GET', 'POST'])
@login_required
def cajero():
    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == 'POST':
        nombre = request.form['nombre']
        membresia = request.form['membresia']
        estado = request.form['estado']
        metodo_pago = request.form['metodo_pago']
        monto = request.form['monto']
        vencimiento = request.form['vencimiento']

        cur.execute("""
            INSERT INTO clientes (nombre, membresia, estado, metodo_pago, monto, vencimiento, gimnasio_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (nombre, membresia, estado, metodo_pago, monto, vencimiento, current_user.id))
        conn.commit()

    cur.execute("SELECT * FROM clientes WHERE gimnasio_id = %s", (current_user.id,))
    clientes = cur.fetchall()
    cur.close()
    conn.close()

    return render_template('auth/cajero.html', clientes=clientes)

@app.route('/mantenimiento', methods=['GET', 'POST'])
@login_required
def mantenimiento():
    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == 'POST':
        nombre = request.form['nombre']
        fecha_ingreso = request.form['fecha_ingreso']
        ult_mantenimiento = request.form['ult_mantenimiento']
        prox_mantenimiento = request.form['prox_mantenimiento']

        cur.execute("""
            INSERT INTO maquina (nombre, fecha_ingreso, ult_mantenimiento, prox_mantenimiento, gimnasio_id)
            VALUES (%s, %s, %s, %s, %s)
        """, (nombre, fecha_ingreso, ult_mantenimiento, prox_mantenimiento, current_user.id))
        conn.commit()

    cur.execute("SELECT * FROM maquina WHERE gimnasio_id = %s", (current_user.id,))
    maquinas = cur.fetchall()
    cur.close()
    conn.close()

    return render_template('auth/mantenimiento.html', maquinas=maquinas)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login_gimnasio'))

@app.route('/agregar_cliente', methods=['POST'])
@login_required
def agregar_cliente():
    datos = request.get_json()
    nombre = datos.get('nombre')
    membresia = datos.get('membresia')
    estado = datos.get('estado')
    metodo_pago = datos.get('metodo_pago')
    monto = datos.get('monto')
    vencimiento = datos.get('vencimiento')

    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO clientes (nombre, membresia, estado, metodo_pago, monto, vencimiento, gimnasio_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id
        """, (nombre, membresia, estado, metodo_pago, monto, vencimiento, current_user.id))
        nuevo_id = cur.fetchone()['id']
        conn.commit()
        cur.close()
        conn.close()

        return jsonify({
            'id': nuevo_id,
            'nombre': nombre,
            'membresia': membresia,
            'estado': estado,
            'metodo_pago': metodo_pago,
            'monto': monto,
            'vencimiento': vencimiento
        })
    except Exception as e:
        conn.rollback()
        cur.close()
        conn.close()
        return jsonify({'error': str(e)}), 500

@app.route('/editar_cliente/<int:id>', methods=['POST'])
@login_required
def editar_cliente(id):
    datos = request.get_json()
    nombre = datos.get('nombre')
    membresia = datos.get('membresia')
    estado = datos.get('estado')
    metodo_pago = datos.get('metodo_pago')
    monto = datos.get('monto')
    vencimiento = datos.get('vencimiento')

    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            UPDATE clientes SET nombre=%s, membresia=%s, estado=%s, metodo_pago=%s, monto=%s, vencimiento=%s
            WHERE id=%s AND gimnasio_id=%s
        """, (nombre, membresia, estado, metodo_pago, monto, vencimiento, id, current_user.id))
        conn.commit()
        cur.close()
        conn.close()

        return jsonify({
            'id': id,
            'nombre': nombre,
            'membresia': membresia,
            'estado': estado,
            'metodo_pago': metodo_pago,
            'monto': monto,
            'vencimiento': vencimiento
        })
    except Exception as e:
        conn.rollback()
        cur.close()
        conn.close()
        return jsonify({'error': str(e)}), 500

@app.route('/eliminar_cliente/<int:id>', methods=['DELETE'])
@login_required
def eliminar_cliente(id):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM clientes WHERE id = %s AND gimnasio_id = %s", (id, current_user.id))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({'success': True})
    except Exception as e:
        conn.rollback()
        cur.close()
        conn.close()
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)