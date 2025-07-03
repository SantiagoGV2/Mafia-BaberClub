-- Crear la base de datos
CREATE DATABASE IF NOT EXISTS barberia_db;
USE barberia_db;

-- Tabla de categorías de servicios (menos dependiente)
CREATE TABLE IF NOT EXISTS categorias_servicios (
    cat_id INT AUTO_INCREMENT PRIMARY KEY,
    cat_nombre VARCHAR(100) NOT NULL,
    cat_descripcion TEXT
);

-- Tabla de servicios
CREATE TABLE IF NOT EXISTS servicios (
    ser_id INT AUTO_INCREMENT PRIMARY KEY,
    ser_nombre VARCHAR(100) NOT NULL,
    ser_descripcion TEXT,
    ser_duracion INT NOT NULL, -- en minutos
    ser_precio DECIMAL(10,2) NOT NULL,
    ser_categoria_id INT,
    ser_estado ENUM('activo', 'inactivo') DEFAULT 'activo',
    FOREIGN KEY (ser_categoria_id) REFERENCES categorias_servicios(cat_id)
);

-- Tabla de barberos
CREATE TABLE IF NOT EXISTS barberos (
    bar_id INT AUTO_INCREMENT PRIMARY KEY,
    bar_nombre VARCHAR(100) NOT NULL,
    bar_email VARCHAR(100) NOT NULL UNIQUE,
    bar_password VARCHAR(255) NOT NULL,
    bar_especialidad VARCHAR(100),
    bar_descripcion TEXT,
    bar_imagen VARCHAR(255),
    bar_estado ENUM('activo', 'inactivo') DEFAULT 'activo',
    bar_fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    bar_ultimo_acceso TIMESTAMP NULL,
    bar_token_recuperacion VARCHAR(255),
    bar_token_expiracion TIMESTAMP,
    bar_intentos_fallidos INT DEFAULT 0,
    bar_bloqueado BOOLEAN DEFAULT FALSE,
    bar_fecha_bloqueo TIMESTAMP NULL
);

-- Tabla de clientes
CREATE TABLE IF NOT EXISTS clientes (
    cli_id INT AUTO_INCREMENT PRIMARY KEY,
    cli_nombre VARCHAR(100) NOT NULL,
    cli_telefono VARCHAR(20) NOT NULL,
    cli_email VARCHAR(100) NOT NULL UNIQUE,
    cli_password VARCHAR(255) NOT NULL,
    cli_fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    cli_estado ENUM('activo', 'inactivo') DEFAULT 'activo',
    cli_token_recuperacion VARCHAR(255),
    cli_token_expiracion TIMESTAMP
);

-- Tabla de horarios de barberos
CREATE TABLE IF NOT EXISTS horarios_barberos (
    hor_id INT AUTO_INCREMENT PRIMARY KEY,
    hor_barbero_id INT NOT NULL,
    hor_dia_semana ENUM('lunes', 'martes', 'miercoles', 'jueves', 'viernes', 'sabado', 'domingo') NOT NULL,
    hor_hora_inicio TIME NOT NULL,
    hor_hora_fin TIME NOT NULL,
    FOREIGN KEY (hor_barbero_id) REFERENCES barberos(bar_id)
);

-- Tabla de reservas (más dependiente)
CREATE TABLE IF NOT EXISTS reservas (
    res_id INT AUTO_INCREMENT PRIMARY KEY,
    res_cliente_id INT NOT NULL,
    res_servicio_id INT NOT NULL,
    res_barbero_id INT NOT NULL,
    res_fecha DATE NOT NULL,
    res_hora_inicio TIME NOT NULL,
    res_hora_fin TIME NOT NULL,
    res_estado ENUM('pendiente', 'confirmada', 'completada', 'cancelada', 'actualizada') DEFAULT 'pendiente',
    res_total_pagar DECIMAL(10,2) NOT NULL,
    res_notas TEXT,
    res_fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    res_fecha_completado TIMESTAMP NULL,
    res_tiempo_real_duracion INT NULL, -- Duración real en minutos
    res_notificacion_enviada BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (res_cliente_id) REFERENCES clientes(cli_id),
    FOREIGN KEY (res_servicio_id) REFERENCES servicios(ser_id),
    FOREIGN KEY (res_barbero_id) REFERENCES barberos(bar_id)
);

-- Insertar datos de ejemplo para categorías
INSERT INTO categorias_servicios (cat_nombre, cat_descripcion) VALUES
('Cortes de Cabello', 'Servicios de corte de cabello tradicionales y modernos'),
('Barba', 'Servicios de afeitado y cuidado de barba'),
('Tratamientos', 'Tratamientos especializados para el cabello');

-- Insertar datos de ejemplo para servicios
INSERT INTO servicios (ser_nombre, ser_descripcion, ser_duracion, ser_precio, ser_categoria_id) VALUES
('Corte Clásico', 'Corte tradicional con tijera y máquina', 45, 25000, 1),
('Afeitado Clásico', 'Afeitado tradicional con navaja', 30, 20000, 2),
('Tratamiento Capilar', 'Tratamiento profundo para el cabello', 60, 35000, 3),
('Diseño de Barba', 'Diseño y modelado de barba', 40, 28000, 2),
('Tintura de Barba', 'Tintura profesional para barba', 45, 32000, 2),
('Corte Infantil', 'Corte especializado para niños', 30, 18000, 1);

-- Insertar datos de ejemplo para barberos
INSERT INTO barberos (bar_nombre, bar_email, bar_password, bar_especialidad, bar_descripcion) VALUES
('Carlos Rodríguez', 'carlos@lamafabarber.com', '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 'Cortes Clásicos', 'Especialista en cortes tradicionales y modernos'),
('Miguel Sánchez', 'miguel@lamafabarber.com', '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 'Barbas', 'Experto en diseño y cuidado de barba'),
('Juan Pérez', 'juan@lamafabarber.com', '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 'Tratamientos', 'Especialista en tratamientos capilares');

-- Insertar horarios de ejemplo para barberos
INSERT INTO horarios_barberos (hor_barbero_id, hor_dia_semana, hor_hora_inicio, hor_hora_fin) VALUES
(1, 'lunes', '09:00', '19:00'),
(1, 'martes', '09:00', '19:00'),
(1, 'miercoles', '09:00', '19:00'),
(1, 'jueves', '09:00', '19:00'),
(1, 'viernes', '09:00', '19:00'),
(1, 'sabado', '09:00', '17:00'),
(2, 'lunes', '09:00', '19:00'),
(2, 'martes', '09:00', '19:00'),
(2, 'miercoles', '09:00', '19:00'),
(2, 'jueves', '09:00', '19:00'),
(2, 'viernes', '09:00', '19:00'),
(2, 'sabado', '09:00', '17:00'),
(3, 'lunes', '09:00', '19:00'),
(3, 'martes', '09:00', '19:00'),
(3, 'miercoles', '09:00', '19:00'),
(3, 'jueves', '09:00', '19:00'),
(3, 'viernes', '09:00', '19:00'),
(3, 'sabado', '09:00', '17:00');

-- Triggers para barberos
DELIMITER //
CREATE TRIGGER actualizar_ultimo_acceso
BEFORE UPDATE ON barberos
FOR EACH ROW
BEGIN
    IF NEW.bar_estado = 'activo' AND OLD.bar_estado != 'activo' THEN
        SET NEW.bar_ultimo_acceso = CURRENT_TIMESTAMP;
    END IF;
END//

CREATE TRIGGER resetear_intentos_fallidos
BEFORE UPDATE ON barberos
FOR EACH ROW
BEGIN
    IF NEW.bar_intentos_fallidos > 0 AND 
       TIMESTAMPDIFF(HOUR, COALESCE(NEW.bar_fecha_bloqueo, OLD.bar_fecha_bloqueo), CURRENT_TIMESTAMP) >= 24 THEN
        SET NEW.bar_intentos_fallidos = 0;
        SET NEW.bar_bloqueado = FALSE;
        SET NEW.bar_fecha_bloqueo = NULL;
    END IF;
END//
DELIMITER ;

-- Triggers para reservas
DELIMITER //
CREATE TRIGGER actualizar_total_reserva
AFTER INSERT ON reservas
FOR EACH ROW
BEGIN
    UPDATE reservas r
    JOIN servicios s ON r.res_servicio_id = s.ser_id
    SET r.res_total_pagar = s.ser_precio
    WHERE r.res_id = NEW.res_id;
END//

CREATE TRIGGER actualizar_total_reserva_update
AFTER UPDATE ON reservas
FOR EACH ROW
BEGIN
    IF NEW.res_servicio_id != OLD.res_servicio_id THEN
        UPDATE reservas r
        JOIN servicios s ON r.res_servicio_id = s.ser_id
        SET r.res_total_pagar = s.ser_precio
        WHERE r.res_id = NEW.res_id;
    END IF;
END//

CREATE TRIGGER actualizar_hora_fin_insert
BEFORE INSERT ON reservas
FOR EACH ROW
BEGIN
    DECLARE duracion_servicio INT;
    
    SELECT ser_duracion INTO duracion_servicio
    FROM servicios
    WHERE ser_id = NEW.res_servicio_id;
    
    SET NEW.res_hora_fin = ADDTIME(NEW.res_hora_inicio, SEC_TO_TIME(duracion_servicio * 60));
END//

CREATE TRIGGER actualizar_hora_fin_update
BEFORE UPDATE ON reservas
FOR EACH ROW
BEGIN
    DECLARE duracion_servicio INT;
    
    IF NEW.res_servicio_id != OLD.res_servicio_id THEN
        SELECT ser_duracion INTO duracion_servicio
        FROM servicios
        WHERE ser_id = NEW.res_servicio_id;
        
        SET NEW.res_hora_fin = ADDTIME(NEW.res_hora_inicio, SEC_TO_TIME(duracion_servicio * 60));
    END IF;
END//

CREATE TRIGGER verificar_disponibilidad_insert
BEFORE INSERT ON reservas
FOR EACH ROW
BEGIN
    DECLARE existe_solapamiento INT;
    
    SELECT COUNT(*) INTO existe_solapamiento
    FROM reservas r
    WHERE r.res_barbero_id = NEW.res_barbero_id
    AND r.res_fecha = NEW.res_fecha
    AND r.res_estado != 'cancelada'
    AND (
        (NEW.res_hora_inicio BETWEEN r.res_hora_inicio AND r.res_hora_fin)
        OR (NEW.res_hora_fin BETWEEN r.res_hora_inicio AND r.res_hora_fin)
        OR (r.res_hora_inicio BETWEEN NEW.res_hora_inicio AND NEW.res_hora_fin)
    );
    
    IF existe_solapamiento > 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'El barbero no está disponible en ese horario';
    END IF;
END//

CREATE TRIGGER verificar_disponibilidad_update
BEFORE UPDATE ON reservas
FOR EACH ROW
BEGIN
    DECLARE existe_solapamiento INT;
    
    IF NEW.res_hora_inicio != OLD.res_hora_inicio OR NEW.res_servicio_id != OLD.res_servicio_id THEN
        SELECT COUNT(*) INTO existe_solapamiento
        FROM reservas r
        WHERE r.res_barbero_id = NEW.res_barbero_id
        AND r.res_fecha = NEW.res_fecha
        AND r.res_id != NEW.res_id
        AND r.res_estado != 'cancelada'
        AND (
            (NEW.res_hora_inicio BETWEEN r.res_hora_inicio AND r.res_hora_fin)
            OR (NEW.res_hora_fin BETWEEN r.res_hora_inicio AND r.res_hora_fin)
            OR (r.res_hora_inicio BETWEEN NEW.res_hora_inicio AND NEW.res_hora_fin)
        );
        
        IF existe_solapamiento > 0 THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'El barbero no está disponible en ese horario';
        END IF;
    END IF;
END//
DELIMITER ; 