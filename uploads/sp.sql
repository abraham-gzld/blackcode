DELIMITER //

CREATE PROCEDURE InsertarVentaConDetalles(
    IN p_usuario_id INT,
    IN p_total DOUBLE,
    IN p_metodo_pago VARCHAR(20),
    IN p_status VARCHAR(15),
    IN p_data JSON
)
BEGIN
    DECLARE v_venta_id INT;

    -- Insertar en la tabla venta
    INSERT INTO venta (usuario_id, fecha, total, metodo_pago, status)
    VALUES (p_usuario_id, CURDATE(), p_total, p_metodo_pago, p_status);

    -- Obtener el ID de la venta insertada
    SET v_venta_id = LAST_INSERT_ID();

    -- Insertar los detalles de la venta desde el JSON
 INSERT INTO venta_detalle (venta_id, articulo_id, cantidad, sub_total)
SELECT 
    v_venta_id,
    d.articulo_id,  -- ✅ Accede directamente a la columna generada
    d.cantidad,
    d.sub_total
FROM JSON_TABLE(p_data, '$[*]' COLUMNS (
    articulo_id INT PATH '$.articulo_id',
    cantidad INT PATH '$.cantidad',
    sub_total DOUBLE PATH '$.sub_total'
)) AS d;

    -- Retornar el ID de la venta insertada
    SELECT v_venta_id AS venta_id;
END //

DELIMITER ;

DROP PROCEDURE IF EXISTS InsertarVentaConDetalles;

DELIMITER //

CREATE PROCEDURE InsertarVentaConDetalles(
    IN p_usuario_id INT,
    IN p_total DOUBLE,
    IN p_metodo_pago VARCHAR(20),
    IN p_status VARCHAR(15),
    IN p_data JSON
)
BEGIN
    DECLARE v_venta_id INT;

    -- Insertar en la tabla venta
    INSERT INTO venta (usuario_id, fecha, total, metodo_pago, status)
    VALUES (p_usuario_id, CURDATE(), p_total, p_metodo_pago, p_status);

    -- Obtener el ID de la venta insertada
    SET v_venta_id = LAST_INSERT_ID();

    -- Insertar los detalles de la venta desde el JSON
    INSERT INTO venta_detalle (venta_id, articulo_id, cantidad, sub_total)
    SELECT 
        v_venta_id,
        d.articulo_id,
        d.cantidad,
        d.sub_total
    FROM JSON_TABLE(p_data, '$[*]' COLUMNS (
        articulo_id INT PATH '$.articulo_id',
        cantidad INT PATH '$.cantidad',
        sub_total DOUBLE PATH '$.sub_total'
    )) AS d;

    -- Insertar en la bitácora (registrando la venta)
    INSERT INTO bitacora (usuario_id, venta_id, accion, fecha, descripcion)
    VALUES (p_usuario_id, v_venta_id, 'Venta registrada', CURDATE(), 'La venta fue registrada con éxito.');

    -- Insertar en la tabla de distribución (dejando los campos faltantes como NULL)
    INSERT INTO distribucion (venta_id, articulo_id, cantidad, fecha_envio, direccion, status)
    SELECT 
        v_venta_id,
        d.articulo_id,
        d.cantidad,
        NULL,  -- No tenemos la fecha de envío, dejamos NULL
        NULL,  -- No tenemos la dirección, dejamos NULL
        NULL   -- No tenemos el status, dejamos NULL
    FROM JSON_TABLE(p_data, '$[*]' COLUMNS (
        articulo_id INT PATH '$.articulo_id',
        cantidad INT PATH '$.cantidad'
    )) AS d;

    -- Retornar el ID de la venta insertada
    SELECT v_venta_id AS venta_id;
END //

DELIMITER ;








##############################?///////////////////////
DELIMITER //

CREATE PROCEDURE AceptarVenta(
    IN p_venta_id INT, 
    IN p_usuario_id INT
)
BEGIN
    DECLARE v_articulo_id INT;
    DECLARE v_cantidad INT;
    DECLARE v_total DOUBLE;
    DECLARE done INT DEFAULT FALSE;
    DECLARE cur CURSOR FOR 
        SELECT articulo_id, cantidad
        FROM Venta_detalle
        WHERE venta_id = p_venta_id;

    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;

    -- Iniciar la transacción
    START TRANSACTION;

    -- 1. Obtener el total de la venta para usarlo en la bitácora
    SELECT total INTO v_total
    FROM Venta
    WHERE id = p_venta_id;

    -- 2. Actualizar el estado de la venta a "Aceptada"
    UPDATE Venta
    SET status = 'Aceptada'
    WHERE id = p_venta_id;

    -- 3. Descontar la cantidad de artículos vendidos en el inventario
    OPEN cur;

    -- Descontar artículo por artículo
    read_loop: LOOP
        FETCH cur INTO v_articulo_id, v_cantidad;
        IF done THEN
            LEAVE read_loop;
        END IF;

        -- Descontar la cantidad de artículos vendidos
        UPDATE Inventario
        SET cantidad = cantidad - v_cantidad
        WHERE articulo_id = v_articulo_id;

    END LOOP;

    CLOSE cur;

    -- 4. Insertar en la bitácora que la venta ha sido aceptada
    INSERT INTO Bitacora (usuario_id, venta_id, accion, fecha, descripcion)
    VALUES (p_usuario_id, p_venta_id, 'Venta Aceptada', NOW(), CONCAT('La venta con ID ', p_venta_id, ' ha sido aceptada. Total: ', v_total));

    -- Si todo sale bien, confirmar la transacción
    COMMIT;

END //

DELIMITER ;

