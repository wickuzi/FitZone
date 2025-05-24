from flask import Flask, render_template, request, redirect, url_for, flash,session
from config import config
from flask_mysqldb import MySQL
from flask_session import Session
from flask_login import LoginManager, login_user, logout_user, login_required
import MySQLdb.cursors
from flask import jsonify

app = Flask(__name__)
app.config.from_object(config['development'])

mysql = MySQL(app)

ROLES = {
    'cajero': 'cajero123',
    'mantenimiento': 'mante123'
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

@app.route('/cajero', methods=['GET', 'POST'])
def cajero():
    if 'rol' not in session or session['rol'] != 'cajero':
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        nombre = request.form['nombre']
        membresia = request.form['membresia']
        estado = request.form['estado']
        metodo_pago = request.form['metodo_pago']
        monto = request.form['monto']
        vencimiento = request.form['vencimiento']

        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO clientes (nombre, membresia, estado, metodo_pago, monto, vencimiento)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (nombre, membresia, estado, metodo_pago, monto, vencimiento))
        mysql.connection.commit()

        return redirect(url_for('cajero'))
    
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT * FROM clientes")
    clientes = cur.fetchall()
    cur.close()


    return render_template('auth/cajero.html', clientes=clientes)

@app.route('/editar_cliente/<int:id>', methods=['POST'])
def editar_cliente(id):
    datos = request.get_json()
    cur = mysql.connection.cursor()
    cur.execute("""
        UPDATE clientes
        SET nombre=%s, membresia=%s, estado=%s, metodo_pago=%s, monto=%s, vencimiento=%s
        WHERE id=%s
    """, (
        datos['nombre'],
        datos['membresia'],
        datos['estado'],
        datos['metodo_pago'],
        datos['monto'],
        datos['vencimiento'],
        id
    ))
    mysql.connection.commit()
    cur.close()
    return jsonify(datos)


@app.route('/agregar_cliente', methods=['POST'])
def agregar_cliente():
    data = request.get_json()

    nombre = data['nombre']
    membresia = data['membresia']
    estado = data['estado']
    metodo_pago = data['metodo_pago']
    monto = data['monto']
    vencimiento = data['vencimiento']

    cur = mysql.connection.cursor()
    cur.execute("""
        INSERT INTO clientes (nombre, membresia, estado, metodo_pago, monto, vencimiento)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (nombre, membresia, estado, metodo_pago, monto, vencimiento))
    mysql.connection.commit()

    nuevo_id = cur.lastrowid
    cur.close()

    return jsonify({
        "id": nuevo_id,
        "nombre": nombre,
        "membresia": membresia,
        "estado": estado,
        "metodo_pago": metodo_pago,
        "monto": monto,
        "vencimiento": vencimiento
    })

@app.route('/eliminar_cliente/<int:id>', methods=['DELETE'])
def eliminar_cliente(id):
    try:
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM clientes WHERE id = %s", (id,))
        mysql.connection.commit()
        cur.close()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@app.route('/mantenimiento', methods=['GET', 'POST'])
def mantenimiento():
    if 'rol' not in session or session['rol'] != 'mantenimiento':
        return redirect(url_for('login'))
    
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    if request.method == 'POST':
        nombre = request.form['nombre']
        fecha_ingreso = request.form['fecha_ingreso']
        ult_mantenimiento = request.form['ult_mantenimiento']
        prox_mantenimiento = request.form['prox_mantenimiento']

        cur.execute("""
            INSERT INTO maquina (nombre, fecha_ingreso, ult_mantenimiento, prox_mantenimiento)
            VALUES (%s, %s, %s, %s)
        """, (nombre, fecha_ingreso, ult_mantenimiento, prox_mantenimiento))
        mysql.connection.commit()
        return redirect(url_for('mantenimiento'))

    cur.execute("SELECT * FROM maquina")
    maquinas = cur.fetchall()
    cur.close()

    return render_template('auth/mantenimiento.html', maquinas=maquinas)

@app.route('/editar_maquina/<int:id>', methods=['POST'])
def editar_maquina(id):
    data = request.get_json()
    cur = mysql.connection.cursor()

    cur.execute("""
        UPDATE maquina
        SET nombre = %s,
            fecha_ingreso = %s,
            ult_mantenimiento = %s,
            prox_mantenimiento = %s
        WHERE id = %s
    """, (
        data['nombre'],
        data['fecha_ingreso'],
        data['ult_mantenimiento'],
        data['prox_mantenimiento'],
        id
    ))
    mysql.connection.commit()
    cur.close()

    return jsonify(data)

@app.route('/eliminar_maquina/<int:id>', methods=['DELETE'])
def eliminar_maquina(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM maquina WHERE id = %s", (id,))
    mysql.connection.commit()
    cur.close()
    return '', 204

@app.route('/agregar_maquina', methods=['POST'])
def agregar_maquina():
    data = request.get_json()
    cur = mysql.connection.cursor()

    cur.execute("""
        INSERT INTO maquina (nombre, fecha_ingreso, ult_mantenimiento, prox_mantenimiento)
        VALUES (%s, %s, %s, %s)
    """, (
        data['nombre'],
        data['fecha_ingreso'],
        data['ult_mantenimiento'],
        data['prox_mantenimiento']
    ))

    mysql.connection.commit()
    nuevo_id = cur.lastrowid
    cur.close()

    data['id'] = nuevo_id
    return jsonify(data)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.config.from_object(config['development'])
    app.run()