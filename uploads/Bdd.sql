-- Creación de la Base de Datos
CREATE DATABASE Negocios;
USE Negocios;

DROP DATABASE Negocios;
DROP TABLE Clientes;

-- Tabla: Usuarios
CREATE TABLE Usuarios (
    id INT PRIMARY KEY auto_increment,
    email varchar(30) not null unique,
    username VARCHAR(35),
    password VARCHAR(20),
    rol ENUM('Cliente', 'Compras', 'Ventas', 'Almacen', 'Logistica', 'Proveedor', 'Administrador') DEFAULT 'Cliente', 
    departamento VARCHAR(15),
    nombres VARCHAR(35),
    apellido_paterno VARCHAR(25),
    apellido_materno VARCHAR(20),
    RFC VARCHAR(30),
    codigo_postal VARCHAR(5),
    calle VARCHAR(35),
    numero_interior INT,
    numero_exterior INT,
    colonia VARCHAR(30),
    ciudad VARCHAR(30),
    status VARCHAR(15)
);
-- Tabla: Proveedores
CREATE TABLE Proveedores (
    id INT PRIMARY KEY auto_increment,
    nombre VARCHAR(45),
    telefono DOUBLE,
    email VARCHAR(45),
    direccion VARCHAR(45)
);

-- Tabla: Categorias_Articulos
CREATE TABLE Categorias_Articulos (
    id INT PRIMARY KEY auto_increment,
    nombre VARCHAR(25) NOT NULL
);

-- Tabla: Articulos
CREATE TABLE Articulos (
    id INT PRIMARY KEY AUTO_INCREMENT,
    descripcion VARCHAR(35),
    categoria_id INT,
    costo DOUBLE,
    precio DOUBLE,
    impuesto DOUBLE,
    existencia INT,
    status VARCHAR(15),
    provedor_id INT,
    imagen VARCHAR(255),
    FOREIGN KEY (provedor_id) REFERENCES Proveedores(id),
    FOREIGN KEY (categoria_id) REFERENCES Categorias_Articulos(id)
);

-- Tabla: Inventario
CREATE TABLE Inventario (
    id INT PRIMARY KEY auto_increment,
    articulo_id INT,
    cantidad INT,
    status VARCHAR(15),
    FOREIGN KEY (articulo_id) REFERENCES Articulos(id)
);

-- Tabla: Venta
CREATE TABLE Venta (
    id INT PRIMARY KEY auto_increment,
    usuario_id INT,  -- Usuario que registra la venta
    fecha DATE,
    total DOUBLE,
    metodo_pago VARCHAR(25),
    status VARCHAR(15),
    FOREIGN KEY (usuario_id) REFERENCES Usuarios(id)
);

-- Tabla: Venta_detalle
CREATE TABLE Venta_detalle (
    id INT PRIMARY KEY auto_increment,
    venta_id INT,
    articulo_id INT,
    cantidad INT,
    sub_total DOUBLE,
    FOREIGN KEY (venta_id) REFERENCES Venta(id),
    FOREIGN KEY (articulo_id) REFERENCES Articulos(id)
);

-- Tabla: Compra
CREATE TABLE Compra (
    id INT PRIMARY KEY auto_increment,
    proveedor_id INT,
    usuario_id INT,
    fecha DATE,
    total DOUBLE,
    status VARCHAR(15),
    FOREIGN KEY (proveedor_id) REFERENCES Proveedores(id),
    FOREIGN KEY (usuario_id) REFERENCES Usuarios(id)
);

-- Tabla: Detalle_Compra
CREATE TABLE Detalle_Compra (
    id INT PRIMARY KEY auto_increment,
    compra_id INT,
    articulo_id INT,
    cantidad INT,
    sub_total DOUBLE,
    FOREIGN KEY (compra_id) REFERENCES Compra(id),
    FOREIGN KEY (articulo_id) REFERENCES Articulos(id)
);

-- Tabla: Distribucion
CREATE TABLE Distribucion (
    id INT PRIMARY KEY auto_increment,
    venta_id INT,  -- Venta asociada a la distribución
    articulo_id INT,
    cantidad INT,
    fecha_envio DATE,
    direccion VARCHAR(45),
    status VARCHAR(15),
    FOREIGN KEY (venta_id) REFERENCES Venta(id),
    FOREIGN KEY (articulo_id) REFERENCES Articulos(id)
);

-- Tabla: Requisiciones
CREATE TABLE Requisiciones (
    id INT PRIMARY KEY auto_increment,
    usuario_id INT,  -- Usuario que genera la requisición
    fecha DATE,
    status VARCHAR(15),
    FOREIGN KEY (usuario_id) REFERENCES Usuarios(id)
);

-- Tabla: Requisiciones_detalle
CREATE TABLE Requisiciones_detalle (
    id INT PRIMARY KEY auto_increment,
    requisicion_id INT,
    articulo_id INT,
    cantidad INT,
    FOREIGN KEY (requisicion_id) REFERENCES Requisiciones(id),
    FOREIGN KEY (articulo_id) REFERENCES Articulos(id)
);

-- Tabla: Cotizaciones
CREATE TABLE Cotizaciones (
    id INT PRIMARY KEY auto_increment,
    usuario_id INT,  -- Usuario que genera la cotización
    proveedor_id INT,  -- Proveedor al que se le solicita la cotización
    fecha DATE,
    status VARCHAR(15),
    FOREIGN KEY (usuario_id) REFERENCES Usuarios(id),
    FOREIGN KEY (proveedor_id) REFERENCES Proveedores(id)
);

-- Tabla: Cotizaciones_detalle
CREATE TABLE Cotizaciones_detalle (
    id INT PRIMARY KEY auto_increment,
    cotizacion_id INT,
    articulo_id INT,
    cantidad INT,
    precio_unitario DOUBLE,
    FOREIGN KEY (cotizacion_id) REFERENCES Cotizaciones(id),
    FOREIGN KEY (articulo_id) REFERENCES Articulos(id)
);

-- Tabla: Bitacora
CREATE TABLE Bitacora (
    id INT PRIMARY KEY auto_increment,
    usuario_id INT,  -- Usuario que realiza la acción
    venta_id INT,  -- Venta relacionada (opcional)
    compra_id INT,  -- Compra relacionada (opcional)
    distribucion_id INT,  -- Distribución relacionada (opcional)
    accion VARCHAR(50),
    fecha DATETIME,
    descripcion TEXT,
    FOREIGN KEY (usuario_id) REFERENCES Usuarios(id),
    FOREIGN KEY (venta_id) REFERENCES Venta(id),
    FOREIGN KEY (compra_id) REFERENCES Compra(id),
    FOREIGN KEY (distribucion_id) REFERENCES Distribucion(id)
);