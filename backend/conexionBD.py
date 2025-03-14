import pymysql

def obtener_conexion():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="dimas123",
        database="negocios"
    )