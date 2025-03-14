create database blackcode;
use blackcode;

CREATE TABLE productos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    categoria VARCHAR(100) NOT NULL,
    costo DECIMAL(10,2) NOT NULL,
    precio DECIMAL(10,2) NOT NULL,
    existencia INT NOT NULL DEFAULT 0,
    status ENUM('Stock', 'Sin Stock') DEFAULT 'Stock',
    impuesto DECIMAL(5,2) DEFAULT 0.00,
    imagen VARCHAR(255) NOT NULL 
);