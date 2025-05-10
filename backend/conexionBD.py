import pymysql

def obtener_conexion():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="dimas123",
        database="negocios"
    )
def obtener_conexion_banco():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="dimas123",
        database="banco"
    )