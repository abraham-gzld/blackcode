import datetime
from flask import Flask, json, render_template, request, redirect, url_for, session, flash,jsonify
import pymysql, os 
import pymysql.cursors
from werkzeug.utils import secure_filename
from conexionBD import obtener_conexion, obtener_conexion_banco
from datetime import datetime
from collections import defaultdict

app = Flask("BlackCode")
app.secret_key = "tu_clave_secreta"
app.secret_key
import os


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conexion = obtener_conexion()
        cursor = conexion.cursor()

        query = "SELECT id, email, password, username, rol FROM usuarios WHERE email = %s AND password = %s"
        cursor.execute(query, (email, password))
        usuario = cursor.fetchone()

        cursor.close()
        conexion.close()

        if usuario:
            id, email, password, username, rol = usuario  # ✅ orden correcto

            session["user_id"] = id
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
            if rol == "Compras":
                return redirect(url_for("compras"))
            if rol == "RH":
                return redirect(url_for("nominas"))
        return "Usuario o Contraseña incorrectos", 401  
    return render_template("login.html")


@app.route('/perfil')
def perfil():
    if 'user_id' not in session:
        return redirect(url_for('login'))  # Redirige si no está logeado

    user_id = session['user_id']
    conexion = obtener_conexion()
    cursor = conexion.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM Usuarios WHERE id = %s", (user_id,))
    usuario = cursor.fetchone()
    cursor.close()
    conexion.close()

    return render_template('edit_usuario.html', usuario=usuario)



@app.route("/actualizar_perfil", methods=["POST"])
def actualizar_perfil():
    if "user_id" not in session:
        flash("Debes iniciar sesión para editar tu perfil.", "warning")
        return redirect(url_for("login"))

    id_usuario = session["user_id"]

    # Obtener datos del formulario
    email = request.form["email"]
    username = request.form["username"]
    nombres = request.form["nombres"]
    apellido_paterno = request.form["apellido_paterno"]
    apellido_materno = request.form["apellido_materno"]
    RFC = request.form["RFC"]
    codigo_postal = request.form["codigo_postal"]
    calle = request.form["calle"]
    numero_interior = request.form["numero_interior"]
    numero_exterior = request.form["numero_exterior"]
    colonia = request.form["colonia"]
    ciudad = request.form["ciudad"]

    # Conexión a la base de datos
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    # Actualizar usuario
    consulta = """
        UPDATE usuarios
        SET email = %s, username = %s, nombres = %s,
            apellido_paterno = %s, apellido_materno = %s, RFC = %s,
            codigo_postal = %s, calle = %s, numero_interior = %s,
            numero_exterior = %s, colonia = %s, ciudad = %s
        WHERE id = %s
    """
    valores = (
        email, username, nombres, apellido_paterno, apellido_materno,
        RFC, codigo_postal, calle, numero_interior,
        numero_exterior, colonia, ciudad, id_usuario
    )

    cursor.execute(consulta, valores)
    conexion.commit()

    cursor.close()
    conexion.close()

    # También puedes actualizar el username en la sesión por si cambia
    session["username"] = username

    flash("Tu perfil ha sido actualizado exitosamente.", "success")
    return redirect(url_for("perfil"))



@app.route("/reporte_ventas")
def reporte_ventas():
    conexion = obtener_conexion()
    cursor = conexion.cursor(pymysql.cursors.DictCursor)
    
    fecha_inicio = request.args.get("fecha_inicio")
    fecha_fin = request.args.get("fecha_fin")
    
    query = """
        SELECT 
            v.id AS venta_id,
            v.fecha,
            u.username,
            v.metodo_pago,
            v.total,
            vd.articulo_id,
            a.descripcion AS articulo,
            vd.cantidad,
            vd.sub_total
        FROM Venta v
        JOIN Usuarios u ON v.usuario_id = u.id
        JOIN Venta_detalle vd ON vd.venta_id = v.id
        JOIN Articulos a ON vd.articulo_id = a.id
        WHERE v.status = 'Pedido entregado'
    """
    
    params = []
    if fecha_inicio and fecha_fin:
        query += " AND v.fecha BETWEEN %s AND %s"
        params.extend([fecha_inicio, fecha_fin])
    
    query += " ORDER BY v.fecha DESC"
    
    cursor.execute(query, params)
    resultados = cursor.fetchall()
    
    cursor.close()
    conexion.close()

    # Agrupar por venta_id
    ventas_agrupadas = defaultdict(lambda: {"detalles": []})
    for row in resultados:
        venta_id = row["venta_id"]
        if "fecha" not in ventas_agrupadas[venta_id]:
            ventas_agrupadas[venta_id].update({
                "fecha": row["fecha"],
                "username": row["username"],
                "metodo_pago": row["metodo_pago"],
                "total": row["total"]
            })
        ventas_agrupadas[venta_id]["detalles"].append({
            "articulo": row["articulo"],
            "cantidad": row["cantidad"],
            "sub_total": row["sub_total"]
        })

    return render_template("reporte_ventas.html", ventas=ventas_agrupadas, fecha_inicio=fecha_inicio, fecha_fin=fecha_fin)
    
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
        return redirect(url_for('almacen'))  

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


@app.route('/producto/<int:producto_id>')
def producto_detalle(producto_id):
    conexion = obtener_conexion()
    with conexion.cursor(pymysql.cursors.DictCursor) as cursor:
        cursor.execute("SELECT * FROM articulos WHERE id = %s", (producto_id,))
        producto = cursor.fetchone()

    if producto is None:
        return "Producto no encontrado", 404
    
    username = session.get('username', None)

    return render_template('producto_detalle.html', producto=producto, username= username)




@app.route("/")
def hello_word():
    conexion = obtener_conexion()
    cursor = conexion.cursor(pymysql.cursors.DictCursor)

    # Obtener productos de la BDD
    cursor.execute("SELECT * FROM Articulos WHERE categoria_id = 2")
    productos = cursor.fetchall()
    cursor.close()
    conexion.close()
    return render_template("index.html", productos = productos)

@app.route('/carrito')
def ver_carrito():
    return render_template('carrito.html')

@app.route('/compras', methods=['GET', 'POST'])
def compras():
    if 'username' not in session:
        print("❌ No hay usuario en sesión")
        return redirect(url_for('login'))

    username = session['username']
    conexion = obtener_conexion()
    cursor = conexion.cursor(pymysql.cursors.DictCursor)

    # Obtener proveedores y artículos
    cursor.execute("SELECT * FROM Proveedores")
    proveedores = cursor.fetchall()

    cursor.execute("SELECT * FROM Articulos")
    articulos = cursor.fetchall()

    if request.method == 'POST':
        proveedor_id = request.form['proveedor']
        usuario_id = 1  # Cambia esto por el usuario autenticado
        fecha = datetime.now().strftime('%Y-%m-%d')
        total = 0

        # Insertar en la tabla Compra
        cursor.execute("""
            INSERT INTO Compra (proveedor_id, usuario_id, fecha, total, status)
            VALUES (%s, %s, %s, %s, %s)
        """, (proveedor_id, usuario_id, fecha, total, 'Pendiente'))
        conexion.commit()

        compra_id = cursor.lastrowid
        detalles = []

        # Insertar en la tabla Detalle_Compra
        for key, value in request.form.items():
            if 'cantidad_' in key and int(value) > 0:
                articulo_id = key.split('_')[1]
                cantidad = int(value)

                # Obtener precio del artículo
                cursor.execute("SELECT costo FROM Articulos WHERE id = %s", (articulo_id,))
                articulo = cursor.fetchone()
                if articulo:
                    subtotal = cantidad * articulo['costo']
                    total += subtotal
                    detalles.append((compra_id, articulo_id, cantidad, subtotal))

        cursor.executemany("""
            INSERT INTO Detalle_Compra (compra_id, articulo_id, cantidad, sub_total)
            VALUES (%s, %s, %s, %s)
        """, detalles)

        # Actualizar el total en la compra
        cursor.execute("UPDATE Compra SET total = %s WHERE id = %s", (total, compra_id))
        conexion.commit()

        flash("Compra realizada correctamente", "success")
        return redirect(url_for('compras'))

    # Obtener compras existentes
    cursor.execute("""
    SELECT c.id, c.fecha, c.total, c.status, p.nombre AS proveedor, 
           GROUP_CONCAT(a.descripcion, ' - ', d.cantidad, ' unidades' SEPARATOR '<br>') AS detalles
    FROM Compra c
    JOIN Proveedores p ON c.proveedor_id = p.id
    JOIN Detalle_Compra d ON c.id = d.compra_id
    JOIN Articulos a ON d.articulo_id = a.id
    GROUP BY c.id
    ORDER BY c.fecha DESC
    """)
    compras = cursor.fetchall()

    cursor.close()
    conexion.close()
    return render_template('compras.html', proveedores=proveedores, articulos=articulos, compras=compras)

@app.route("/almacen_view_compras")
def almacen_view_compras():
    conexion = obtener_conexion()
    cursor = conexion.cursor(pymysql.cursors.DictCursor)
    
    # Ejecutar consulta para obtener las compras/ventas desde la base de datos
    cursor.execute("""
        SELECT c.id, c.fecha, c.total, c.status, p.nombre AS proveedor, 
               GROUP_CONCAT(a.descripcion, ' - ', d.cantidad, ' unidades' SEPARATOR '<br>') AS articulo, 
               GROUP_CONCAT(d.cantidad SEPARATOR '<br>') AS cantidad
        FROM Compra c
        JOIN Proveedores p ON c.proveedor_id = p.id
        JOIN Detalle_Compra d ON c.id = d.compra_id
        JOIN Articulos a ON d.articulo_id = a.id
        GROUP BY c.id
        ORDER BY c.fecha DESC
    """)
    
    compras = cursor.fetchall()
    
    cursor.close()
    conexion.close()

    return render_template("almacen_view_compras.html", compras=compras)


@app.route("/almacen/agregar/<int:compra_id>", methods=["POST"])
def agregar_a_almacen(compra_id):
    # Conectar a la base de datos
    conexion = obtener_conexion()
    cursor = conexion.cursor(pymysql.cursors.DictCursor)
    
    # Obtener la información de la compra
    cursor.execute("SELECT * FROM Compra WHERE id = %s", (compra_id,))
    compra = cursor.fetchone()
    
    if compra:
        # Obtener los detalles de la compra (artículos y cantidades)
        cursor.execute("""
            SELECT d.articulo_id, d.cantidad
            FROM Detalle_Compra d
            WHERE d.compra_id = %s
        """, (compra_id,))
        detalles = cursor.fetchall()
        
        # Procesar cada artículo y agregar la cantidad al almacén
        for detalle in detalles:
            articulo_id = detalle['articulo_id']
            cantidad = detalle['cantidad']
            
            # Actualizar la existencia del artículo sumando la cantidad
            cursor.execute("""
                UPDATE Articulos
                SET existencia = existencia + %s
                WHERE id = %s
            """, (cantidad, articulo_id))
        
        # Cambiar el estado de la compra a "Aceptada" (si es necesario)
        cursor.execute("UPDATE Compra SET status = %s WHERE id = %s", ('Aceptada', compra_id))
        
        # Confirmar los cambios
        conexion.commit()

        flash("Artículo(s) agregado(s) al almacén correctamente", "success")
    else:
        flash("Compra no encontrada", "danger")

    # Cerrar la conexión y redirigir a la página de compras
    cursor.close()
    conexion.close()

    return redirect(url_for('almacen_view_compras'))


@app.route("/ver_compras")
def ver_compras():
    conexion = obtener_conexion()
    cursor = conexion.cursor(pymysql.cursors.DictCursor)
    
    cursor.execute("""
        SELECT c.id, c.fecha, c.total, c.status, 
               p.nombre AS proveedor, 
               a.descripcion AS articulo, 
               d.cantidad 
        FROM Compra c
        JOIN Proveedores p ON c.proveedor_id = p.id
        JOIN Detalle_Compra d ON c.id = d.compra_id
        JOIN Articulos a ON d.articulo_id = a.id
        ORDER BY c.fecha DESC
    """)
    compras = cursor.fetchall()
    
    cursor.close()
    conexion.close()  # Asegurar que la conexión se cierra
    return render_template("ver_compras.html", compras=compras)

@app.route('/compras/cancelar/<int:compra_id>', methods=['POST'])
def cancelar_compra(compra_id):
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    # Verificar si la compra existe y su estado actual
    cursor.execute("SELECT status FROM Compra WHERE id = %s", (compra_id,))
    compra = cursor.fetchone()

    if compra and compra[0] != 'Cancelado':
        # Actualizar el estado de la compra a "Cancelado"
        cursor.execute("UPDATE Compra SET status = 'Cancelado' WHERE id = %s", (compra_id,))
        conexion.commit()
        flash("Compra cancelada correctamente", "success")
    else:
        flash("La compra ya está cancelada o no existe", "danger")

    cursor.close()
    conexion.close()
    return redirect(url_for('compras'))

@app.route('/compras/aceptar/<int:compra_id>', methods=['POST'])
def aceptar_compra(compra_id):
    conexion = obtener_conexion()
    cursor = conexion.cursor(pymysql.cursors.DictCursor)

    # Obtener los detalles de la compra
    cursor.execute("""
        SELECT articulo_id, cantidad 
        FROM Detalle_Compra 
        WHERE compra_id = %s
    """, (compra_id,))
    detalles = cursor.fetchall()

    if not detalles:
        flash("No se encontraron artículos en esta compra", "danger")
        return redirect(url_for('compras'))

    # Sumar las unidades a la columna 'existencia' en la tabla 'Articulos'
    for detalle in detalles:
        cursor.execute("""
            UPDATE Articulos 
            SET existencia = existencia + %s 
            WHERE id = %s
        """, (detalle['cantidad'], detalle['articulo_id']))

    # Cambiar el estado de la compra a 'Aceptado'
    cursor.execute("""
        UPDATE Compra 
        SET status = 'Aceptado' 
        WHERE id = %s
    """, (compra_id,))

    conexion.commit()
    cursor.close()
    conexion.close()

    flash("Compra aceptada y stock actualizado", "success")
    return redirect(url_for('compras'))

@app.route('/compras/agregar', methods=['POST'])
def agregar_compra():
    conexion = obtener_conexion()
    cursor = conexion.cursor(pymysql.cursors.DictCursor)

    proveedor_id = request.form['proveedor']
    articulo_id = request.form['articulo']
    cantidad = int(request.form['cantidad'])
    usuario_id = 1  # Cambiar por el usuario autenticado
    fecha = datetime.now().strftime('%Y-%m-%d')

    # Insertar compra con total en 0 (se actualizará después)
    cursor.execute("""
        INSERT INTO Compra (proveedor_id, usuario_id, fecha, total, status)
        VALUES (%s, %s, %s, %s, %s)
    """, (proveedor_id, usuario_id, fecha, 0, 'Pendiente'))
    conexion.commit()

    compra_id = cursor.lastrowid

    # Obtener precio del artículo según el proveedor
    cursor.execute("SELECT costo FROM Articulos WHERE id = %s", (articulo_id,))
    articulo = cursor.fetchone()

    if articulo:
        subtotal = cantidad * articulo['costo']
        
        # Insertar detalle de la compra
        cursor.execute("""
            INSERT INTO Detalle_Compra (compra_id, articulo_id, cantidad, sub_total)
            VALUES (%s, %s, %s, %s)
        """, (compra_id, articulo_id, cantidad, subtotal))

        # Actualizar el total en la tabla Compra
        cursor.execute("UPDATE Compra SET total = %s WHERE id = %s", (subtotal, compra_id))
        conexion.commit()

    cursor.close()
    conexion.close()

    flash("Pedido agregado correctamente", "success")
    return redirect(url_for('compras'))


@app.route('/dashboard')
def dashboard():
    print("Sesión actual:", session)  # 🔴 Depuración en la consola

    if 'username' in session:
        username = session['username']
        return render_template('dashboard.html', username=username)
    else:
        print("❌ No hay usuario en sesión")
        return redirect(url_for('login'))
    

@app.route('/ver_usuarios')
def ver_usuarios():
    conexion = obtener_conexion()
    cursor = conexion.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM usuarios")
    usuarios = cursor.fetchall()
    conexion.close()
    return render_template('ver_usuarios.html', usuarios=usuarios)

@app.route('/usuarios/agregar', methods=['GET', 'POST'])
def agregar_usuario():
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        rol = request.form['rol']
        departamento = request.form['departamento']
        nombres = request.form['nombres']
        apellido_paterno = request.form['apellido_paterno']
        apellido_materno = request.form['apellido_materno']
        RFC = request.form['RFC']
        codigo_postal = request.form['codigo_postal']
        calle = request.form['calle']
        numero_interior = request.form['numero_interior']
        numero_exterior = request.form['numero_exterior']
        colonia = request.form['colonia']
        ciudad = request.form['ciudad']
        status = request.form['status']

        conexion = obtener_conexion()
        cursor = conexion.cursor(pymysql.cursors.DictCursor)
        cursor.execute("""
            INSERT INTO Usuarios (email, username, password, rol, departamento, nombres, apellido_paterno, apellido_materno, RFC, codigo_postal, calle, numero_interior, numero_exterior, colonia, ciudad, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (email, username, password, rol, departamento, nombres, apellido_paterno, apellido_materno, RFC, codigo_postal, calle, numero_interior, numero_exterior, colonia, ciudad, status))
        
        conexion.commit()
        cursor.close()
        conexion.close()
        flash("Usuario agregado correctamente", "success")
        return redirect(url_for('ver_usuarios'))

    return render_template('agregar_usuario.html')

@app.route('/usuarios/editar/<int:id>', methods=['GET'])
def editar_usuario(id):
    conexion = obtener_conexion()
    cursor = conexion.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM usuarios WHERE id = %s", (id,))
    usuario = cursor.fetchone()
    conexion.close()
    return render_template('editar_usuario.html', usuario=usuario)

@app.route('/usuarios/actualizar/<int:id>', methods=['POST'])
def actualizar_usuario(id):
    email = request.form['email']
    username = request.form['username']
    rol = request.form['rol']
    nombres = request.form['nombres']
    apellido_paterno = request.form['apellido_paterno']
    apellido_materno = request.form['apellido_materno']
    RFC = request.form['RFC']
    codigo_postal = request.form['codigo_postal']
    calle = request.form['calle']
    numero_interior = request.form['numero_interior']
    numero_exterior = request.form['numero_exterior']
    colonia = request.form['colonia']
    ciudad = request.form['ciudad']
    status = request.form['status']

    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute("""
        UPDATE usuarios SET 
            email = %s, username = %s, rol = %s, nombres = %s, apellido_paterno = %s, 
            apellido_materno = %s, RFC = %s, codigo_postal = %s, calle = %s, 
            numero_interior = %s, numero_exterior = %s, colonia = %s, ciudad = %s, status = %s
        WHERE id = %s
    """, (email, username, rol, nombres, apellido_paterno, apellido_materno, RFC, 
          codigo_postal, calle, numero_interior, numero_exterior, colonia, ciudad, status, id))
    
    conexion.commit()
    conexion.close()
    return redirect(url_for('ver_usuarios'))


@app.route('/usuarios/eliminar/<int:id>', methods=['GET'])
def eliminar_usuario(id):
    try:
        conexion = obtener_conexion()
        with conexion.cursor() as cursor:
            cursor.execute("DELETE FROM usuarios WHERE id = %s", (id,))
        conexion.commit()
        flash(f'Usuario con ID {id} eliminado correctamente', 'success')
    except Exception as e:
        conexion.rollback()
        flash(f'Error al eliminar el usuario: {str(e)}', 'danger')
    finally:
        conexion.close()

    return redirect(url_for('ver_usuarios'))  # Redirige a la lista de usuarios

@app.route('/articulos')
def ver_articulos():
    conexion = obtener_conexion()
    cursor = conexion.cursor(pymysql.cursors.DictCursor)
    cursor.execute("SELECT * FROM articulos")
    articulos = cursor.fetchall()
    conexion.close()
    return render_template('articulos.html', articulos=articulos)

@app.route('/articulos/agregar', methods=['GET', 'POST'])
def agregar_articulo():
    conexion = obtener_conexion()
    cursor = conexion.cursor(pymysql.cursors.DictCursor)

    # Obtener categorías y proveedores desde la base de datos
    cursor.execute("SELECT * FROM categorias_articulos")
    categorias = cursor.fetchall()
    
    cursor.execute("SELECT * FROM proveedores")  # Asegúrate de tener esta tabla
    proveedores = cursor.fetchall()

    if request.method == 'POST':
        descripcion = request.form['descripcion']
        precio = float(request.form['precio'])  # Convertir a float
        costo = float(request.form['costo'])  # Convertir a float
        stock = int(request.form['stock'])  # Convertir a int
        imagen = request.form['imagen']
        categoria_id = int(request.form['categoria'])  # Convertir a int
        proveedor_id = int(request.form['id_proveedor'])  # Convertir a int
        status = request.form['status']  # Puede ser un string o un número

        cursor.execute("""
        INSERT INTO articulos (descripcion, precio, costo, existencia, imagen, categoria_id, provedor_id, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (descripcion, precio, costo, stock, imagen, categoria_id, proveedor_id, status))

        conexion.commit()
        cursor.close()
        conexion.close()
        
        flash("Artículo agregado correctamente", "success")
        return redirect(url_for('ver_articulos'))  # Asegúrate de que esta función existe

    cursor.close()
    conexion.close()
    return render_template('agregar_articulo.html', categorias=categorias, proveedores=proveedores)



@app.route('/articulos/editar/<int:id>', methods=['GET', 'POST'])
def editar_articulo(id):
    conexion = obtener_conexion()
    cursor = conexion.cursor(pymysql.cursors.DictCursor)

    # Obtener el artículo a editar
    cursor.execute("SELECT * FROM articulos WHERE id = %s", (id,))
    articulo = cursor.fetchone()

    # Obtener todas las categorías
    cursor.execute("SELECT * FROM categorias_articulos")
    categorias = cursor.fetchall()

    if request.method == 'POST':
        descripcion = request.form['descripcion']
        precio = request.form['precio']
        stock = request.form['stock']
        imagen = request.form['imagen']
        categoria_id = request.form['categoria']

        cursor.execute("""
            UPDATE articulos 
            SET  descripcion=%s, precio=%s, existencia=%s, imagen=%s, categoria_id=%s
            WHERE id=%s
        """, (descripcion, precio, stock, imagen, categoria_id, id))

        conexion.commit()
        cursor.close()
        conexion.close()
        flash("Artículo actualizado correctamente", "success")
        return redirect(url_for('ver_articulos'))

    cursor.close()
    conexion.close()

    return render_template('editar_articulo.html', articulo=articulo, categorias=categorias)


@app.route('/articulos/eliminar/<int:id>', methods=['GET', 'POST'])
def eliminar_articulo(id):
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    cursor.execute("DELETE FROM articulos WHERE id = %s", (id,))
    conexion.commit()

    cursor.close()
    conexion.close()

    flash("Artículo eliminado correctamente", "success")
    return redirect(url_for('ver_articulos'))



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
        carrito[str(id)]['cantidad'] += 1 
    else:
        carrito[str(id)] = {
            'descripcion': producto['descripcion'],  
            'precio': producto['precio'],
            'imagen': producto['imagen'],
            'cantidad': 1
        }

    session.modified = True  # Guardar cambios en la sesión

    return redirect(url_for('mostrar_carrito'))  # 🔹 Se cambió para evitar error de nombre de endpoint

# Carrito
@app.route('/ver_carrito')
def mostrar_carrito():
    if 'username' in session:
        username = session['username']
        carrito = session.get('carrito', {})

        conexion = obtener_conexion()
        with conexion.cursor() as cursor:
            cursor.execute("SELECT estado_destino, costo FROM costos_envio ORDER BY estado_destino")
            resultados = cursor.fetchall()
            estados = [fila[0] for fila in resultados]
            costos_envio = {fila[0]: float(fila[1]) for fila in resultados}

        return render_template('carrito.html', carrito=carrito, username=username, estados=estados, costos_envio=costos_envio)
    else:
        return redirect(url_for('login'))

@app.route('/eliminar_carrito/<int:id>', methods=['POST'])
def eliminar_carrito(id):
    carrito = session.get('carrito', {})
    id_str = str(id)
    print(f"Carrito antes de eliminar el id {id}:", carrito)  # Log antes de eliminar
    if id_str in carrito:
        del carrito[id_str]
        session['carrito'] = carrito
        session.modified = True
        print(f"Carrito después de eliminar el id {id}:", carrito)  # Log después de eliminar
    else:
        print(f"El id {id} no estaba en el carrito")
    return jsonify({'success': True})

@app.route('/actualizar_carrito', methods=['POST'])
def actualizar_carrito():
    data = request.get_json()
    producto_id = str(data.get('id'))
    nueva_cantidad = int(data.get('cantidad'))

    if 'carrito' in session and producto_id in session['carrito']:
        session['carrito'][producto_id]['cantidad'] = nueva_cantidad
        session.modified = True
        return {'status': 'ok'}
    else:
        return {'status': 'error', 'message': 'Producto no encontrado en el carrito'}, 404



@app.route('/procesar_pago', methods=['POST'])
def procesar_pago():
    if 'carrito' not in session or not session['carrito']:
        return jsonify({'success': False, 'message': 'El carrito está vacío'}), 400

    if 'usuario' not in session:
        return jsonify({'success': False, 'message': 'Usuario no autenticado'}), 401

    cliente_email = session['usuario']
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute("SELECT id FROM usuarios WHERE email = %s", (cliente_email,))
    usuario = cursor.fetchone()
    if not usuario:
        cursor.close()
        conexion.close()
        return jsonify({'success': False, 'message': 'Usuario no encontrado'}), 404

    usuario_id = usuario[0]
    metodo_pago = request.form.get('metodo_pago')
    estado_destino = request.form.get('estado_destino')

    if not metodo_pago:
        return jsonify({'success': False, 'message': 'Método de pago no especificado'}), 400

    carrito = session['carrito']
    total_productos = sum(int(prod['cantidad']) * float(prod['precio']) for prod in carrito.values())

    # IVA del 16%
    total_iva = total_productos * 0.16

    # Costo de envío según estado
    if estado_destino == 'Sinaloa':
        envio = 0
    else:
        cursor.execute("SELECT costo FROM costos_envio WHERE estado_destino = %s", (estado_destino,))
        envio_data = cursor.fetchone()
        envio = float(envio_data[0]) if envio_data else 0

    # Total final
    total_final = total_productos + total_iva + envio

    if metodo_pago == 'Tarjeta':
        num_tarjeta = request.form.get('num_tarjeta')
        nombre_titular = request.form.get('nombre_titular')
        cvv = request.form.get('cvv')
        fecha_exp = request.form.get('fecha_exp')

        if not all([num_tarjeta, nombre_titular, cvv, fecha_exp]):
            return jsonify({'success': False, 'message': 'Datos de tarjeta incompletos'}), 400

        conexion_banco = obtener_conexion_banco()
        cursor_banco = conexion_banco.cursor()

        cursor_banco.execute("""
            SELECT saldo FROM tarjetas 
            WHERE num_tarjeta = %s AND nombre_titular = %s AND cvv = %s AND fecha = %s
        """, (num_tarjeta, nombre_titular, cvv, fecha_exp))

        tarjeta = cursor_banco.fetchone()

        if not tarjeta:
            cursor_banco.close()
            conexion_banco.close()
            return jsonify({'success': False, 'message': 'Tarjeta no válida o no registrada'}), 400

        saldo_actual = float(tarjeta[0])

        if saldo_actual < total_final:
            cursor_banco.close()
            conexion_banco.close()
            return jsonify({'success': False, 'message': 'Saldo insuficiente'}), 400

    # Procesar venta
    status = "Pendiente"

    # Calcular el total de artículos para distribuir envío proporcionalmente
    total_cantidades = sum(int(prod['cantidad']) for prod in carrito.values())

    # Generar detalle con IVA y envío proporcional
    detalles_venta = []
    for id, producto in carrito.items():
        cantidad = int(producto['cantidad'])
        precio = float(producto['precio'])
        sub_total = cantidad * precio
        iva = sub_total * 0.16
        envio_proporcional = (cantidad / total_cantidades) * envio if total_cantidades > 0 else 0
        total_item = sub_total + iva + envio_proporcional

        detalles_venta.append({
            "articulo_id": int(id),
            "cantidad": cantidad,
            "precio_unitario": precio,
            "sub_total": round(sub_total, 2),
            "iva": round(iva, 2),
            "envio": round(envio_proporcional, 2),
            "total": round(total_item, 2)
        })

    detalles_json = json.dumps(detalles_venta)

    try:
        args = (usuario_id, total_final, metodo_pago, status, detalles_json, 0)
        cursor.callproc("InsertarVentaConDetalles", args)

        # Recuperar el valor del parámetro OUT (índice 5)
        cursor.execute("SELECT @_InsertarVentaConDetalles_5")
        venta_id = cursor.fetchone()[0]


        if metodo_pago == 'Tarjeta':
            nuevo_saldo = saldo_actual - total_final
            cursor_banco.execute("""
                UPDATE tarjetas SET saldo = %s 
                WHERE num_tarjeta = %s AND nombre_titular = %s AND cvv = %s AND fecha = %s
            """, (nuevo_saldo, num_tarjeta, nombre_titular, cvv, fecha_exp))
            conexion_banco.commit()

        conexion.commit()
        session['carrito'] = {}
        session.modified = True

        return jsonify({'success': True, 'redirect_url': url_for('detalle_compra', venta_id=venta_id)})

    except Exception as e:
        conexion.rollback()
        if metodo_pago == 'Tarjeta':
            conexion_banco.rollback()
        return jsonify({'success': False, 'message': f"Error en la compra: {str(e)}"}), 500

    finally:
        cursor.close()
        conexion.close()
        if metodo_pago == 'Tarjeta':
            cursor_banco.close()
            conexion_banco.close()


@app.route('/detalle_compra/<int:venta_id>')
def detalle_compra(venta_id):
    conexion = obtener_conexion()
    cursor = conexion.cursor(pymysql.cursors.DictCursor)

    # Obtener datos generales de la venta
    cursor.execute("""
        SELECT v.id AS venta_id, v.fecha, v.total, v.metodo_pago, v.status,
               u.username AS nombre_usuario
        FROM venta v
        JOIN usuarios u ON v.usuario_id = u.id
        WHERE v.id = %s
    """, (venta_id,))
    venta = cursor.fetchone()

    # Obtener detalles de los productos
    cursor.execute("""
        SELECT vd.articulo_id, a.descripcion AS nombre_articulo, vd.cantidad, vd.sub_total
        FROM venta_detalle vd
        JOIN articulos a ON vd.articulo_id = a.id
        WHERE vd.venta_id = %s
    """, (venta_id,))
    detalles = cursor.fetchall()

    cursor.close()
    conexion.close()

    if not venta:
        return "Venta no encontrada", 404

    return render_template("detalle_compra.html", venta=venta, detalles=detalles)


def obtener_detalles_de_venta(venta_id, usuario_id):
    conexion = obtener_conexion()
    try:
        with conexion.cursor(dictionary=True) as cursor:
            # Verifica que la venta pertenezca al usuario
            cursor.execute("""
                SELECT v.id, v.fecha, v.total, v.status
                FROM Venta v
                WHERE v.id = %s AND v.usuario_id = %s
            """, (venta_id, usuario_id))
            venta = cursor.fetchone()

            if not venta:
                return None

            # Obtener detalles de artículos
            cursor.execute("""
                SELECT a.nombre, a.descripcion, dv.cantidad, dv.sub_total
                FROM DetalleVenta dv
                JOIN Articulo a ON dv.articulo_id = a.id
                WHERE dv.venta_id = %s
            """, (venta_id,))
            articulos = cursor.fetchall()

            venta['articulos'] = articulos
            return venta
    finally:
        conexion.close()


@app.route('/pedidos')
def ver_pedidos():
    if 'usuario' not in session:
        return redirect(url_for('login'))  # Redirige si no ha iniciado sesión

    cliente_email = session['usuario']
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute("SELECT id FROM usuarios WHERE email = %s", (cliente_email,))
    usuario = cursor.fetchone()
    cursor.close()
    conexion.close()

    if not usuario:
        return "Usuario no encontrado", 404

    usuario_id = usuario[0]
    pedidos = obtener_pedidos_por_usuario(usuario_id)
    return render_template('pedidos.html', pedidos=pedidos)

def obtener_pedidos_por_usuario(usuario_id):
    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            cursor.execute("""
                SELECT v.id AS venta_id, v.fecha, v.total, v.status
                FROM Venta v
                WHERE v.usuario_id = %s
                ORDER BY v.fecha DESC
            """, (usuario_id,))
            return cursor.fetchall()  # Devuelve una lista de diccionarios
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