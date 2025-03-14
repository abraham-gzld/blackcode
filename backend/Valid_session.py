from flask import session, redirect, url_for
from conexionBD import obtener_conexion  # Asegúrate de importar tu función de conexión

def validar_usuario(email, password):
    conexion = obtener_conexion()
    cursor = conexion.cursor()

    query = "SELECT email, password, rol FROM usuarios WHERE email = %s AND password = %s"
    cursor.execute(query, (email, password))
    usuario = cursor.fetchone()

    cursor.close()
    conexion.close()

    if usuario:
        email, password, rol = usuario
        session["email"] = email
        session["password"] = password
        session["rol"] = rol

        if rol == "Administrador":
            return redirect(url_for("dashboard"))
        elif rol == "Cliente":
            return redirect(url_for("cliente"))
        elif rol == "Vendedor":
            return redirect(url_for("vendedor"))

    return "Usuario o Contraseña incorrectos", 401
