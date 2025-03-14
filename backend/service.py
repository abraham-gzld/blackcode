from flask import Flask, json, render_template, request, redirect, url_for, session, flash,jsonify
import pymysql
from conexionBD import obtener_conexion
from Valid_session import validar_usuario

app = Flask("BlackCode")
app.secret_key = "tu_clave_secreta"

@app.route("/")
def hello_word():
    return render_template("index.html")

@app.route('/carrito')
def ver_carrito():
    return render_template('carrito.html')

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conexion = obtener_conexion()
        cursor = conexion.cursor()

        query = "SELECT email, password, username, rol FROM usuarios WHERE email = %s AND password = %s"
        cursor.execute(query, (email, password))
        usuario = cursor.fetchone()

        cursor.close()
        conexion.close()

        if usuario:
            email, password, username, rol = usuario  # 🔹 Desempaquetado corregido
            
            session["usuario"] = email  
            session["username"] = username  
            session["rol"] = rol  

            if rol == "Administrador":
                return redirect(url_for("dashboard"))
            elif rol == "Cliente":
                return redirect(url_for("cliente"))
            elif rol == "Ventas":
                return redirect(url_for("vendedor"))  
        return "Usuario o Contraseña incorrectos", 401  
    return render_template("login.html")
@app.route('/vendedor')
def vendedor():
    conexion = obtener_conexion()
    cursor = conexion.cursor(pymysql.cursors.DictCursor)

    if 'username' in session:
        username = session['username']
        # Consulta para obtener las solicitudes de venta con los clientes desde usuarios
    query = """
        SELECT v.id AS venta_id, v.fecha, v.total, v.metodo_pago, v.status,
       u.nombres AS cliente, u2.username AS vendedor
        FROM venta v
        JOIN usuarios u ON v.usuario_id = u.id AND u.rol = 'Cliente'
        JOIN usuarios u2 ON v.usuario_id = u2.id
        WHERE v.status = 'Pendiente'
        ORDER BY v.fecha DESC;

    """
    cursor.execute(query)
    ventas = cursor.fetchall()

    cursor.close()
    conexion.close()

    return render_template("vendedor.html", ventas=ventas, username= username)
 
    


    

@app.route('/cliente')
def cliente():
    conexion = obtener_conexion()
    cursor = conexion.cursor(pymysql.cursors.DictCursor)

    # Obtener productos de la BDD
    cursor.execute("SELECT * FROM Articulos WHERE categoria_id = 2")
    productos = cursor.fetchall()
    cursor.close()
    conexion.close()

    if 'username' in session:
        username = session['username']
        return render_template('cliente.html', username=username, productos=productos)
    else:
        print("❌ No hay usuario en sesión")
        return redirect(url_for('login'))

@app.route('/agregar_carrito/<int:id>', methods=['POST'])
def agregar_carrito(id):
    conexion = obtener_conexion()
    cursor = conexion.cursor(pymysql.cursors.DictCursor)  # 🔹 Usa un cursor de diccionario

    # Consulta para obtener el producto de la base de datos
    query = "SELECT id, descripcion, precio, imagen FROM articulos WHERE id = %s"
    cursor.execute(query, (id,))
    producto = cursor.fetchone()  # Ahora devuelve un diccionario

    cursor.close()
    conexion.close()

    if not producto:
        return "Producto no encontrado", 404  # Evita agregar un producto inexistente

    if 'carrito' not in session:
        session['carrito'] = {}

    carrito = session['carrito']

    # Accede a los valores con claves en lugar de índices
    if str(id) in carrito:
        carrito[str(id)]['cantidad'] += 1  # Si ya está en el carrito, incrementa la cantidad
    else:
        carrito[str(id)] = {
            'descripcion': producto['descripcion'],  # 🔹 Ahora accede con clave
            'precio': producto['precio'],
            'imagen': producto['imagen'],
            'cantidad': 1
        }

    session.modified = True  # Guardar cambios en la sesión

    return redirect(url_for('mostrar_carrito'))  # 🔹 Se cambió para evitar error de nombre de endpoint

# Carrito
@app.route('/ver_carrito')
def mostrar_carrito():
    carrito = session.get('carrito', {})  # Obtiene el carrito de la sesión o un diccionario vacío
    return render_template('carrito.html', carrito=carrito)
@app.route('/eliminar_carrito/<int:id>', methods=['POST'])
def eliminar_carrito(id):
    carrito = session.get('carrito', {})  
    id_str = str(id)  

    if id_str in carrito:
        del carrito[id_str]  # Eliminar el producto del carrito
        session['carrito'] = carrito  
        session.modified = True  

    return jsonify({'success': True})


@app.route('/procesar_pago', methods=['POST'])
def procesar_pago():
    if 'carrito' not in session or not session['carrito']:
        return jsonify({'success': False, 'message': 'El carrito está vacío'}), 400
    
    if 'usuario' not in session:
        return jsonify({'success': False, 'message': 'Usuario no autenticado'}), 401

    cliente_email = session['usuario']  

    conexion = obtener_conexion()
    cursor = conexion.cursor()

    # Obtener el ID del usuario a partir del email
    query_usuario = "SELECT id FROM usuarios WHERE email = %s"
    cursor.execute(query_usuario, (cliente_email,))
    usuario = cursor.fetchone()

    if not usuario:
        cursor.close()
        conexion.close()
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404

    usuario_id = usuario[0]
    
    # Datos de la venta
    metodo_pago = "Tarjeta"  
    status = "Pendiente"
    
    carrito = session['carrito']
    total = sum(int(prod['cantidad']) * float(prod['precio']) for prod in carrito.values())

    # Crear JSON para `p_data`
    detalles_venta = [
        {
            "articulo_id": int(id),
            "cantidad": int(producto["cantidad"]),
            "sub_total": float(producto["cantidad"]) * float(producto["precio"])
        }
        for id, producto in carrito.items()
    ]

    detalles_json = json.dumps(detalles_venta)  # Convertir a JSON

    try:
        # Llamar al procedimiento almacenado
        cursor.callproc("InsertarVentaConDetalles", 
            (usuario_id, total, metodo_pago, status, detalles_json))
        
        # Obtener el ID de la venta insertada
        cursor.execute("SELECT LAST_INSERT_ID()")
        venta_id = cursor.fetchone()[0]

        conexion.commit()

        session['carrito'] = {}  # Vaciar el carrito después de la compra
        session.modified = True
        mensaje = f"Compra realizada con éxito. ID Venta: {venta_id}"

    except Exception as e:
        conexion.rollback()
        mensaje = f"Error en la compra: {str(e)}"

    finally:
        cursor.close()
        conexion.close()

    return jsonify({'success': True, 'message': mensaje, 'venta_id': venta_id})

def actualizar_estado(venta_id, nuevo_estado):
    # Conexión a la base de datos
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    
    try:
        # Actualizar el estado de la venta en la base de datos
        sql = "UPDATE venta SET status = %s WHERE id = %s"
        cursor.execute(sql, (nuevo_estado, venta_id))
        
        # Confirmar los cambios (commit en la conexión, no en el cursor)
        conexion.commit()

    finally:
        cursor.close()
        conexion.close()  # Aseguramos de cerrar la conexión también



# Función para llamar al procedimiento almacenado de MySQL
def aceptar_venta(venta_id, usuario_id):
    # Conectar a la base de datos
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            # Llamar al procedimiento almacenado AceptarVenta
            cursor.callproc('AceptarVenta', [venta_id, usuario_id])

            # Confirmar cambios (commit)
            conexion.commit()

    except pymysql.MySQLError as err:
        # Manejar errores de MySQL
        print(f"Error: {err}")
    finally:
        conexion.close()


@app.route('/actualizar_estado_venta/<int:venta_id>', methods=['POST'])
def actualizar_estado_venta(venta_id):
    accion = request.form.get('accion')
    usuario_id = 1  # Asumimos que el usuario actual es el que hace la acción, aquí deberías obtener el ID del usuario de la sesión o del formulario.

    if accion == 'aceptar':
        nuevo_estado = 'Aceptada'
        
        # Llamar a la función que ejecuta el procedimiento almacenado
        aceptar_venta(venta_id, usuario_id)
        
    elif accion == 'rechazar':
        nuevo_estado = 'Rechazada'
        # Aquí puedes actualizar el estado de la venta si es necesario, por ejemplo, en la base de datos.
        # No llamamos al procedimiento porque la lógica es diferente.

    else:
        return redirect(url_for('ventas'))  # Redirigir a la lista de ventas si no se pasa una acción válida

    # Redirigir de vuelta a la página de ventas con el estado actualizado
    return redirect(url_for('vendedor'))

if __name__ == "__main__":
    app.run(debug=True)

@app.route('/dashboard')
def dashboard():
    print("Sesión actual:", session)  # 🔴 Depuración en la consola

    if 'username' in session:
        username = session['username']
        return render_template('dashboard.html', username=username)
    else:
        print("❌ No hay usuario en sesión")
        return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
