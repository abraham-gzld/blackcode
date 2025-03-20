from flask import Flask, json, render_template, request, redirect, url_for, session, flash,jsonify
import pymysql, os 
from werkzeug.utils import secure_filename
from conexionBD import obtener_conexion

app = Flask("BlackCode")
app.secret_key = "tu_clave_secreta"
app.secret_key
import os

@app.route('/almacen_editar_articulo/<int:id>')
def almacen_actualizar_articulo(id):
    conexion = obtener_conexion()
    cursor = conexion.cursor(pymysql.cursors.DictCursor)

    query = """
        SELECT id, descripcion, categoria_id, costo, precio, impuesto, existencia, status, provedor_id
        FROM Articulos
        WHERE id = %s
    """
    cursor.execute(query, (id,))
    articulo = cursor.fetchone()

    cursor.close()
    conexion.close()

    if not articulo:
        flash('Artículo no encontrado', 'danger')
        return redirect(url_for('almacen'))  # Redirige si el artículo no existe

    return render_template('almacen_editar_articulo.html', articulo=articulo)

@app.route('/almacen_editar_articulo/<int:id>', methods=['GET', 'POST'])
def almacen_editar_articulo(id):
    if 'username' not in session or session.get('rol') not in ['Administrador', 'Almacen']:
        flash('Acceso no autorizado', 'danger')
        return redirect(url_for('login'))

    conexion = obtener_conexion()
    cursor = conexion.cursor(pymysql.cursors.DictCursor)

    if request.method == 'POST':
        # Obtener datos del formulario
        descripcion = request.form['descripcion']
        categoria_id = request.form['categoria_id']
        costo = request.form['costo']
        precio = request.form['precio']
        impuesto = request.form['impuesto']
        existencia = request.form['existencia']
        status = request.form['status']
        proveedor_id = request.form['provedor_id']

        # Actualizar en la BD
        query = """
            UPDATE Articulos
            SET descripcion = %s, categoria_id = %s, costo = %s, precio = %s, 
                impuesto = %s, existencia = %s, status = %s, provedor_id = %s
            WHERE id = %s
        """
        valores = (descripcion, categoria_id, costo, precio, impuesto, existencia, status, proveedor_id, id)
        cursor.execute(query, valores)
        conexion.commit()

        flash('Artículo actualizado correctamente', 'success')
        return redirect(url_for('almacen'))

    # Si es GET, obtener los datos del artículo para mostrarlos en el formulario
    query = "SELECT * FROM Articulo WHERE id = %s"
    cursor.execute(query, (id,))
    articulo = cursor.fetchone()

    cursor.close()
    conexion.close()

    return render_template('almacen_editar_articulo.html', articulo=articulo)



@app.route('/logistica_actualizar_estatus/<int:id>', methods=['POST'])
def logistica_actualizar_estatus(id):
    if 'username' not in session or session.get('rol') not in ['Administrador', 'Logistica']:
        return jsonify({'success': False, 'error': 'Acceso no autorizado'}), 403

    data = request.get_json()
    nuevo_estatus = data.get('estatus')

    if not nuevo_estatus:
        return jsonify({'success': False, 'error': 'Estatus inválido'}), 400

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        # Llamada al procedimiento almacenado con ID del pedido y nuevo estatus
        cursor.callproc('sp_actualizar_estatus_pedido', (id, nuevo_estatus, session['username']))
        
        conexion.commit()
        cursor.close()
        conexion.close()

        return jsonify({'success': True, 'message': 'Estatus actualizado correctamente'})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500




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
            if rol == "Logistica":
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
    



@app.route("/almacen_view_pedidos")
def almacen_view_pedidos():
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    # Obtener las ventas aceptadas
    query = "SELECT id, usuario_id, fecha, total, metodo_pago, status FROM venta WHERE status = 'Aceptada'"
    cursor.execute(query)
    columnas = [col[0] for col in cursor.description]  
    ventas = [dict(zip(columnas, fila)) for fila in cursor.fetchall()]  

    cursor.close()
    conexion.close()

    return render_template("almacen_view_pedidos.html", ventas=ventas)

@app.route("/detalle_venta/<int:venta_id>")
def detalle_venta(venta_id):
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    # Obtener detalles de la venta específica
    query = """
    SELECT a.nombre AS producto, v.cantidad, a.precio
    FROM venta_detalle v
    JOIN articulo a ON v.articulo_id = a.id
    WHERE v.venta_id = %s
    """
    cursor.execute(query, (venta_id,))
    
    columnas = [col[0] for col in cursor.description]
    detalles = [dict(zip(columnas, fila)) for fila in cursor.fetchall()]

    cursor.close()
    conexion.close()

    return jsonify(detalles)
@app.route("/obtener_detalles/<int:venta_id>")
def obtener_detalles(venta_id):
    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        query = """
            SELECT 
                IFNULL(a.descripcion, 'Sin nombre') AS producto, 
                IFNULL(v.cantidad, 0) AS cantidad, 
                IFNULL(a.precio, 0.00) AS precio
            FROM Venta_detalle v
            JOIN Articulos a ON v.articulo_id = a.id
            WHERE v.venta_id = %s
        """
        cursor.execute(query, (venta_id,))

        # Obtener las columnas
        columnas = [col[0] for col in cursor.description]
        
        # Convertir la respuesta a una lista de diccionarios
        detalles = [dict(zip(columnas, fila)) for fila in cursor.fetchall()]

        cursor.close()
        conexion.close()

        if not detalles:
            return jsonify({"error": "No se encontraron detalles"}), 404

        return jsonify(detalles)  # ✅ Devuelve siempre JSON válido
    except Exception as e:
        print("Error en la API:", e)  # 👀 Para depuración en la terminal
        return jsonify({"error": str(e)}), 500  # 🔴 Devuelve el error real para ver en la API

@app.route('/finalizar_pedido', methods=['POST'])
def finalizar_pedido():
    try:
        data = request.json
        venta_id = data['venta_id']
        usuario_id = data['usuario_id']  # Debes obtener el usuario logueado
        
        conn = obtener_conexion()
        cursor = conn.cursor()

        # Llamar al procedimiento almacenado
        cursor.callproc('procesar_pedido', (venta_id, usuario_id))

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"mensaje": "Pedido procesado correctamente"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

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
@app.route("/almacen_acepta_pedido/<int:venta_id>", methods=["POST"])
def almacen_acepta_pedido(venta_id):
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    try:
        # Llamar al procedimiento almacenado
        cursor.callproc("almacenAceptaVenta", (venta_id,))
        conexion.commit()

        flash("Pedido aceptado y eliminado correctamente.", "success")
    except Exception as e:
        conexion.rollback()
        flash(f"Error al aceptar el pedido: {str(e)}", "danger")
    finally:
        cursor.close()
        conexion.close()

    return redirect(url_for("almacen_view_pedidos")) 

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

@app.route("/pedidos_aceptados")
def pedidos_aceptados():
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute("SELECT * FROM venta WHERE status = 'Aceptada'")
    ventas = cursor.fetchall()

    cursor.close()
    conexion.close()

    return render_template("pedidos_aceptados.html", ventas=ventas)


@app.route("/gestionar_pedido/<int:venta_id>/<accion>", methods=["POST"])
def gestionar_pedido(venta_id, accion):
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    if accion == "rechazar":
        cursor.execute("UPDATE venta SET status = 'Rechazada' WHERE id = %s", (venta_id,))
    elif accion == "finalizar":
        cursor.execute("CALL sp_actualizar_estado_pedido(%s, 'Finalizado')", (venta_id,))

    conexion.commit()
    cursor.close()
    conexion.close()

    return jsonify({"mensaje": "Pedido actualizado correctamente."})


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


@app.route('/logistica_bitacora/<int:pedido_id>')
def logistica_bitacora(pedido_id):
    # Aquí obtienes los datos de la bitácora del pedido
    bitacora = obtener_bitacora_por_pedido(pedido_id)  
    return render_template("bitacora_detalle.html", bitacora=bitacora)

def obtener_bitacora_por_pedido(pedido_id):
    # Conectar a la base de datos y obtener la bitácora del pedido
    conexion = obtener_conexion()
    cursor = conexion.cursor(pymysql.cursors.DictCursor)
    
    query = "SELECT fecha, evento, detalles FROM bitacora WHERE pedido_id = %s ORDER BY fecha DESC"
    cursor.execute(query, (pedido_id,))
    bitacora = cursor.fetchall()
    
    return bitacora


@app.route('/logistica')
def logistica():
    if 'username' not in session or session.get('rol') not in ['Logistica', 'Administrador']:
        flash('Acceso no autorizado', 'danger')
        return redirect(url_for('login'))

    conexion = obtener_conexion()
    cursor = conexion.cursor(pymysql.cursors.DictCursor)

    # Obtener los pedidos con estado "Procesando pedido"
    query = """
        SELECT 
    V.id AS id,
    CONCAT(U.nombres, ' ', U.apellido_paterno) AS cliente,
    CONCAT(U.calle, ', ', U.colonia, ', ', U.ciudad) AS direccion,
    V.status AS estatus
FROM Venta V
INNER JOIN Usuarios U ON V.usuario_id = U.id
WHERE V.status IN ('Procesando pedido', 'Recolectando pedido', 'Pedido recogido', 'Pedido entregado', 'En Ruta');

    """
    cursor.execute(query)
    pedidos = cursor.fetchall()

    cursor.close()
    conexion.close()

    return render_template('logistica.html', username=session['username'], pedidos=pedidos)

@app.route('/logistica_pedidos_recogidos')
def logistica_pedidos_recogidos():
    if 'username' not in session or session.get('rol') not in ['Administrador', 'Logistica']:
        return jsonify({'success': False, 'error': 'Acceso no autorizado'}), 403

    try:
        conexion = obtener_conexion()
        cursor = conexion.cursor(pymysql.cursors.DictCursor)

        # Obtener solo los pedidos con estatus "Pedido recogido"
        cursor.execute("SELECT * FROM Venta WHERE status = 'En Ruta'")
        pedidos = cursor.fetchall()

        cursor.close()
        conexion.close()

        return render_template('logistica_pedidos_recogidos.html', pedidos=pedidos)

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500



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