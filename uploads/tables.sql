create table usuarios(
id_usuario int not null primary key auto_increment, 
nombre varchar(40) not null,
apellido varchar(20) not null,
email varchar(30) not null,
password varchar(15)not null,
rol enum('Cliente','Provedor','Vendedor','Admin','Almacen'),
estatus enum('activo', 'inactivo'),
departamento varchar(30)
);
