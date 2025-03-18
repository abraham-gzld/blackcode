from flask import Flask, json, render_template, request, redirect, url_for, session, flash,jsonify
import pymysql, os 
from werkzeug.utils import secure_filename
from conexionBD import obtener_conexion

app = Flask("BlackCode")
app.secret_key = "tu_clave_secreta"
app.secret_key
import os


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
            elif rol == "Almacen":
                return redirect(url_for("almacen"))
            elif rol == "Logistica":
                return redirect(url_for("logistica")) 
        return "Usuario o Contraseña incorrectos", 401  
    return render_template("login.html")

@app.route('/dashboard')
def dashboard():
    print("Sesión actual:", session)  # 🔴 Depuración en la consola

    if 'username' in session:
        username = session['username']
        return render_template('dashboard.html', username=username)
    else:
        print("❌ No hay usuario en sesión")
        return redirect(url_for('login'))

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

@app.route("/almacen_view_update")
def almacen_update():
    conexion = obtener_conexion()
    cursor = conexion.cursor(pymysql.cursors.DictCursor)  # 🔹 Usa `DictCursor`
    query = "SELECT * FROM Articulos"
    cursor.execute(query)
    articulos = cursor.fetchall()
    cursor.close()
    conexion.close()
    
    return render_template("almacen_view_update.html", articulos=articulos)

# Ruta para actualizar la existencia
@app.route("/actualizar_existencia", methods=["POST"])
def actualizar_existencia():
    datos = request.get_json()
    articulo_id = datos.get("id")
    nueva_existencia = datos.get("existencia")

    if not articulo_id or not isinstance(nueva_existencia, int) or nueva_existencia < 0:
        return jsonify({"success": False, "error": "Datos inválidos"}), 400

    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)
    
    query = "UPDATE Articulos SET existencia = %s WHERE id = %s"
    cursor.execute(query, (nueva_existencia, articulo_id))
    conexion.commit()

    cursor.close()
    conexion.close()

    return jsonify({"success": True})


@app.route("/almacen_view_articulos")
def almacen_articulos():
    conexion = obtener_conexion()
    cursor = conexion.cursor(pymysql.cursors.DictCursor)
    query= "Select * from articulos"

    cursor.execute(query)
    articulos = cursor.fetchall()

    return render_template("almacen_view_articulos.html", articulos = articulos)

UPLOAD_FOLDER = 'static/img'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route("/almacen_view_addArticulos", methods=['GET', 'POST'])
def almacen_add():
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute("SELECT id, nombre FROM Proveedores")
    proveedores = cursor.fetchall()
    proveedores = [{'id': id, 'nombre': nombre} for id, nombre in proveedores]

    cursor.execute("SELECT id, nombre FROM Categorias_Articulos")
    categorias = cursor.fetchall()
    categorias = [{'id': id, 'nombre': nombre} for id, nombre in categorias]

    if request.method == 'POST':
        # Obtener datos del formulario
        descripcion = request.form.get('descripcion')
        categoria_id = request.form.get('categoria')
        proveedor_id = request.form.get('proveedor')
        costo = request.form.get('costo')
        precio = request.form.get('precio')
        existencia = request.form.get('existencia')
        status = request.form.get('status')

        # Manejo de la imagen
        imagen = request.files.get('imagen')
        imagen_filename = None
        if imagen and imagen.filename != '':
            imagen_filename = secure_filename(imagen.filename)
            imagen_path = os.path.join(app.config['UPLOAD_FOLDER'], imagen_filename)
            imagen.save(imagen_path)

        # Validar los datos
        if not descripcion or not categoria_id or not proveedor_id or not costo or not precio or not existencia or not status:
            flash('Todos los campos son obligatorios.', 'danger')
            return redirect(url_for('almacen_add'))

        try:
            # Insertar el nuevo artículo en la base de datos
            query = """
            INSERT INTO Articulos (descripcion, categoria_id, provedor_id, costo, precio, existencia, status, imagen)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """

            cursor.execute(query, (descripcion, categoria_id, proveedor_id, costo, precio, existencia, status, imagen_filename))
            conexion.commit()

            flash('Artículo agregado exitosamente', 'success')
        except Exception as e:
            flash(f'Ocurrió un error: {str(e)}', 'danger')
        finally:
            cursor.close()
            conexion.close()

        return redirect(url_for('almacen_add'))

    return render_template('almacen_view_addArticulos.html', categorias=categorias, proveedores=proveedores)


@app.route('/almacen')
def almacen():
    if 'username' not in session or session.get('rol') != 'Almacen':
        flash('Acceso no autorizado', 'danger')
        return redirect(url_for('login'))

    conexion = obtener_conexion()
    cursor = conexion.cursor(pymysql.cursors.DictCursor)

    # Consulta para mostrar artículos disponibles en el almacén
    query = """
        SELECT A.id, A.descripcion, A.existencia
        FROM Articulos A
        WHERE A.existencia > 0;
        """
    cursor.execute(query)
    articulos = cursor.fetchall()

    cursor.close()
    conexion.close()

    return render_template('almacen.html', username=session['username'], articulos=articulos)

@app.route('/logistica')
def logistica():
    if 'username' not in session or session.get('rol') not in ['Logistica', 'Administrador']:
        flash('Acceso no autorizado', 'danger')
        return redirect(url_for('login'))

    conexion = obtener_conexion()
    cursor = conexion.cursor(pymysql.cursors.DictCursor)

    # Obtener los pedidos de hoy en distribución
    query = """
        SELECT D.id AS distribucion_id,
               D.venta_id,
               V.usuario_id AS cliente_id,
               CONCAT(U.nombres, ' ', U.apellido_paterno) AS cliente,
               U.calle,
               U.colonia,
               U.ciudad,
               D.fecha_envio,
               D.status
        FROM Distribucion D
        INNER JOIN Venta V ON D.venta_id = V.id
        INNER JOIN Usuarios U ON V.usuario_id = U.id
        WHERE D.fecha_envio = CURDATE()
    """
    cursor.execute(query)
    distribuciones = cursor.fetchall()

    cursor.close()
    conexion.close()

    return render_template('logistica.html', username=session['username'], distribuciones=distribuciones)

@app.route("/vendedor_view_user")
def vendedor_view_users():
    conexion = obtener_conexion()
    cursor = conexion.cursor(pymysql.cursors.DictCursor)

    query = "SELECT * FROM Usuarios WHERE rol = 'Cliente'"
    cursor.execute(query)

    clientes = cursor.fetchall()

    cursor.close()  # Llamar a close() como un método
    conexion.close()  # Llamar a close() como un método
    return render_template('vendedor_view_user.html', clientes=clientes)  

@app.route("/vendedor_view_articulo")
def vendedor_view_articulos():
    conexion = obtener_conexion()
    cursor = conexion.cursor(pymysql.cursors.DictCursor)

    query = "SELECT * FROM articulos"
    cursor.execute(query)

    articulos = cursor.fetchall()

    cursor.close()  # Llamar a close() como un método
    conexion.close()  # Llamar a close() como un método
    return render_template('vendedor_view_articulo.html', articulos=articulos)  

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
        mensaje = f"Compra realizada con éxito."

    except Exception as e:
        conexion.rollback()
        mensaje = f"Error en la compra: {str(e)}"

    finally:
        cursor.close()
        conexion.close()

    return jsonify({'success': True, 'message': mensaje, 'venta_id': venta_id})

@app.route('/pedidos')
def ver_pedidos():
    usuario_id = 1  # Aquí deberías obtener el ID del usuario de la sesión
    pedidos = obtener_pedidos_por_usuario(usuario_id)  # Función que recupera los pedidos del usuario
    return render_template('pedidos.html', pedidos=pedidos)

def obtener_pedidos_por_usuario(usuario_id):
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            cursor.execute("""
                SELECT v.id AS venta_id, v.fecha, v.total, v.status
                FROM Venta v
                WHERE v.usuario_id = %s
            """, (usuario_id,))
            return cursor.fetchall()  # Esto devuelve una lista de tuplas
    finally:
        conexion.close()

@app.route('/pedidos/<int:venta_id>')
def ver_detalle_pedido(venta_id):
    detalles = obtener_detalles_pedido(venta_id)  # Función que recupera los detalles del pedido
    estado = obtener_estado_pedido(venta_id)  # Función que recupera el estado del pedido desde la bitácora
    total = calcular_total_pedido(venta_id)  # Función que calcula el total del pedido
    return render_template('detalle_pedido.html', detalles=detalles, estado=estado, venta_id=venta_id, total=total)

def calcular_total_pedido(venta_id):
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            cursor.execute("""
                SELECT SUM(sub_total) 
                FROM Venta_detalle 
                WHERE venta_id = %s
            """, (venta_id,))
            return cursor.fetchone()[0]  # Retorna el total
    finally:
        conexion.close()
        
def obtener_detalles_pedido(venta_id):
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            cursor.execute("""
                SELECT a.descripcion, vd.cantidad, vd.sub_total
                FROM Venta_detalle vd
                JOIN Articulos a ON vd.articulo_id = a.id
                WHERE vd.venta_id = %s
            """, (venta_id,))
            return cursor.fetchall()
    finally:
        conexion.close()

def obtener_estado_pedido(venta_id):
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            cursor.execute("""
                SELECT descripcion
                FROM Bitacora
                WHERE venta_id = %s
                ORDER BY fecha DESC
                LIMIT 1
            """, (venta_id,))
            return cursor.fetchone()
    finally:
        conexion.close()

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
    usuario_id = 1  # Asumimos que el usuario actual es el que hace la acción

    if accion == 'aceptar':
        try:
            aceptar_venta(venta_id, usuario_id)
            flash('La venta ha sido aceptada con éxito.', 'success')
        except Exception as e:
            flash(f'Error al aceptar la venta: {str(e)}', 'danger')
        
    elif accion == 'rechazar':
        try:
            # Aquí puedes actualizar el estado de la venta a "Rechazada"
            rechazar_venta(venta_id, usuario_id)  # Asegúrate de implementar esta función
            flash('La venta ha sido rechazada con éxito.', 'success')
        except Exception as e:
            flash(f'Error al rechazar la venta: {str(e)}', 'danger')

    else:
        flash('Acción no válida.', 'warning')
        return redirect(url_for('ventas'))  

   
    return redirect(url_for('vendedor'))

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
        raise  # Vuelve a lanzar la excepción para que se maneje en la ruta
    finally:
        conexion.close()

# Implementa la función rechazar_venta si es necesario
def rechazar_venta(venta_id, usuario_id):
    # Conectar a la base de datos y actualizar el estado de la venta a "Rechazada"
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True) 

    try:
        with conexion.cursor() as cursor:
            cursor.execute("UPDATE Venta SET status = 'Rechazada' WHERE id = %s", (venta_id,))
            conexion.commit()
    except pymysql.MySQLError as err:
        print(f"Error: {err}")
        raise  # Vuelve a lanzar la excepción para que se maneje en la ruta
    finally:
        conexion.close()

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)