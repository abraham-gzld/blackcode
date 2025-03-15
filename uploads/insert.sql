INSERT INTO Usuarios (email, username, password, rol, departamento, nombres, apellido_paterno, apellido_materno, RFC, codigo_postal, calle, numero_interior, numero_exterior, colonia, ciudad, status) 
VALUES 
('samuel@gmail.com', 'samuelv', '123', 'Cliente', 'Ventas', 'Samuel', 'Vargas', 'Lopez', 'SAVL900101ABC', '80000', 'Av. Reforma', 10, 25, 'Centro', 'Culiacán', 'Activo');

INSERT INTO Usuarios (email, username, password, rol, departamento, nombres, apellido_paterno, apellido_materno, RFC, codigo_postal, calle, numero_interior, numero_exterior, colonia, ciudad, status) 
VALUES 
('carlos@gmail.com', 'carlosl', '123', 'Compras', 'Compras', 'Carlos Serapio', 'Lopez', '', 'CSL920202DEF', '80100', 'Av. Insurgentes', 5, 12, 'Chapultepec', 'Culiacán', 'Activo');

INSERT INTO Usuarios (email, username, password, rol, departamento, nombres, apellido_paterno, apellido_materno, RFC, codigo_postal, calle, numero_interior, numero_exterior, colonia, ciudad, status) 
VALUES 
('abraham@gmail.com', 'abrahamg', '123', 'Administrador', 'TI', 'Abraham', 'Gonzalez', 'Dimas', 'AGD850303GHI', '80200', 'Blvd. Universitarios', 20, 30, 'Las Quintas', 'Culiacán', 'Activo');

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

-- Playeras
INSERT INTO Articulos (descripcion, categoria_id, costo, precio, impuesto, existencia, status, provedor_id, imagen)
VALUES 
('Playera Negra "Hello World"', 1, 150.00, 300.00, 48.00, 50, 'Activo', 1, 'playera_negra_hello_world.jpg'),
('Playera Blanca "Code is Life"', 1, 140.00, 280.00, 44.80, 40, 'Activo', 1, 'playera_blanca_code_is_life.jpg'),
('Playera Gris "Git Commit"', 1, 160.00, 320.00, 51.20, 30, 'Activo', 2, 'playera_gris_git_commit.jpg'),
('Playera Azul "Debugging Mode"', 1, 155.00, 310.00, 49.60, 25, 'Activo', 2, 'playera_azul_debugging_mode.jpg'),
('Playera Negra "404 Not Found"', 1, 145.00, 290.00, 46.40, 35, 'Activo', 3, 'playera_negra_404_not_found.jpg');

-- Sudaderas
INSERT INTO Articulos (descripcion, categoria_id, costo, precio, impuesto, existencia, status, provedor_id, imagen)
VALUES 
('Sudadera Negra "Coffee & Code"', 2, 300.00, 600.00, 96.00, 20, 'Activo', 1, 'sudadera_negra_coffee_code.jpg'),
('Sudadera Gris "Eat Sleep Code Repeat"', 2, 310.00, 620.00, 99.20, 15, 'Activo', 2, 'sudadera_gris_eat_sleep_code.jpg'),
('Sudadera Azul "No Bugs, Just Features"', 2, 320.00, 640.00, 102.40, 10, 'Activo', 3, 'sudadera_azul_no_bugs.jpg');

-- Gorras
INSERT INTO Articulos (descripcion, categoria_id, costo, precio, impuesto, existencia, status, provedor_id, imagen)
VALUES 
('Gorra Negra "Ctrl + Alt + Del"', 3, 100.00, 200.00, 32.00, 30, 'Activo', 1, 'gorra_negra_ctrl_alt_del.jpg'),
('Gorra Azul "Code Mode Activated"', 3, 110.00, 220.00, 35.20, 25, 'Activo', 2, 'gorra_azul_code_mode.jpg');

-- Tazas
INSERT INTO Articulos (descripcion, categoria_id, costo, precio, impuesto, existencia, status, provedor_id, imagen)
VALUES 
('Taza Blanca "Eat Sleep Code Repeat"', 4, 80.00, 160.00, 25.60, 50, 'Activo', 1, 'taza_blanca_eat_sleep_code.jpg'),
('Taza Negra "Code is Life"', 4, 85.00, 170.00, 27.20, 45, 'Activo', 2, 'taza_negra_code_is_life.jpg');

-- Accesorios
INSERT INTO Articulos (descripcion, categoria_id, costo, precio, impuesto, existencia, status, provedor_id, imagen)
VALUES 
('Llavero "Hello World"', 5, 20.00, 40.00, 6.40, 100, 'Activo', 1, 'llavero_hello_world.jpg'),
('Stickers Pack "Programmer Life"', 5, 50.00, 100.00, 16.00, 200, 'Activo', 2, 'stickers_programmer_life.jpg');

select * from articulos
