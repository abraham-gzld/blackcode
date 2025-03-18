INSERT INTO Usuarios (email, username, password, rol, departamento, nombres, apellido_paterno, apellido_materno, RFC, codigo_postal, calle, numero_interior, numero_exterior, colonia, ciudad, status) 
VALUES 
('samuel@gmail.com', 'samuelv', '123', 'Cliente', 'Ventas', 'Samuel', 'Vargas', 'Lopez', 'SAVL900101ABC', '80000', 'Av. Reforma', 10, 25, 'Centro', 'Culiacán', 'Activo');

INSERT INTO Usuarios (email, username, password, rol, departamento, nombres, apellido_paterno, apellido_materno, RFC, codigo_postal, calle, numero_interior, numero_exterior, colonia, ciudad, status) 
VALUES 
('carlossalas@gmail.com', 'samuelv', '123', 'Cliente', 'cliente', 'Carlos', 'Salas', 'Lopez', 'SAVL900101ABC', '80000', 'Av. Reforma', 10, 25, 'Centro', 'Culiacán', 'Activo');

INSERT INTO Usuarios (email, username, password, rol, departamento, nombres, apellido_paterno, apellido_materno, RFC, codigo_postal, calle, numero_interior, numero_exterior, colonia, ciudad, status) 
VALUES 
('carlos@gmail.com', 'carlosl', '123', 'Compras', 'Compras', 'Carlos Serapio', 'Lopez', '', 'CSL920202DEF', '80100', 'Av. Insurgentes', 5, 12, 'Chapultepec', 'Culiacán', 'Activo');

INSERT INTO Usuarios (email, username, password, rol, departamento, nombres, apellido_paterno, apellido_materno, RFC, codigo_postal, calle, numero_interior, numero_exterior, colonia, ciudad, status) 
VALUES 
('abraham@gmail.com', 'abrahamg', '123', 'Administrador', 'TI', 'Abraham', 'Gonzalez', 'Dimas', 'AGD850303GHI', '80200', 'Blvd. Universitarios', 20, 30, 'Las Quintas', 'Culiacán', 'Activo');

INSERT INTO Usuarios (email, username, password, rol, departamento, nombres, apellido_paterno, apellido_materno, RFC, codigo_postal, calle, numero_interior, numero_exterior, colonia, ciudad, status) 
VALUES 
('crisitna@gmail.com', 'Cristina_s', '123', 'Almacen', 'TI', 'Cristina', 'Solis', 'Contreras', 'CSC850303GHI', '80201', 'Blvd. Universitarios', 20, 30, 'Las Quintas', 'Culiacán', 'Activo');

INSERT INTO Usuarios (email, username, password, rol, departamento, nombres, apellido_paterno, apellido_materno, RFC, codigo_postal, calle, numero_interior, numero_exterior, colonia, ciudad, status) 
VALUES 
('belem@gmail.com', 'Maria_Picosa', '123', 'Ventas', 'Tienda', 'Belem', 'Picos', 'Picosa', 'BPP850303GHI', '80200', 'Blvd. Universitarios', 20, 30, 'Las Quintas', 'Culiacán', 'Activo');

select * from articulos;

INSERT INTO Categorias_Articulos (nombre) 
VALUES 
('Camisas'),
('Playeras'),
('Pantalones');


INSERT INTO Proveedores (nombre, telefono, email, direccion) 
VALUES 
('Textiles MX', 6671234567, 'contacto@textilesmx.com', 'Av. Insurgentes #123, Culiacán, Sinaloa'),

('Distribuidora Ropa SA', 6677654321, 'ventas@distribuidoraropeza.com', 'Calle Reforma #456, Culiacán, Sinaloa'),

('Playeras Premium', 6679876543, 'info@playeraspremium.com', 'Blvd. Universitarios #789, Culiacán, Sinaloa');


INSERT INTO Articulos (descripcion, categoria_id, costo, precio, impuesto, existencia, status, provedor_id, imagen) 
VALUES 
('Playera Negra Dev', 2, 150.00, 250.00, 16.00, 50, 'Activo', 1, 'playera_1.jpg'),

('Playera Blanca Code', 2, 140.00, 240.00, 16.00, 40, 'Activo', 2, 'playera_2.jpg'),

('Playera Azul Debug', 2, 160.00, 260.00, 16.00, 30, 'Activo', 3, 'playera_3.jpg');

Select * from articulos;
delete articulos 
from articulos 
where id= 13;