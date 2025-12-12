-- --------------------------------------------------------
-- Host:                         localhost
-- Versión del servidor:         10.4.32-MariaDB - mariadb.org binary distribution
-- SO del servidor:              Win64
-- HeidiSQL Versión:             12.6.0.6765
-- --------------------------------------------------------

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET NAMES utf8 */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;


-- Volcando estructura de base de datos para evcharging
CREATE DATABASE IF NOT EXISTS `evcharging` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci */;
USE `evcharging`;

-- Volcando estructura para tabla evcharging.auditoria
CREATE TABLE IF NOT EXISTS `auditoria` (
  `id_auditoria` int(11) NOT NULL AUTO_INCREMENT,
  `fecha_hora` datetime NOT NULL,
  `ip_origen` varchar(45) DEFAULT NULL,
  `accion` varchar(50) NOT NULL,
  `descripcion` text DEFAULT NULL,
  PRIMARY KEY (`id_auditoria`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Volcando datos para la tabla evcharging.auditoria: ~19 rows (aproximadamente)
DELETE FROM `auditoria`;
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`) VALUES
	(1, '2025-12-11 12:38:09', '::1', 'weather_alert', 'CP 1: Temperatura -10°C - ALERTA POR FRÍO');
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`) VALUES
	(2, '2025-12-11 12:39:12', '::1', 'weather_alert', 'CP 1: Temperatura 17°C - ALERTA FINALIZADA');
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`) VALUES
	(3, '2025-12-11 20:25:15', 'EV_W', 'weather_alert', 'NORMALIZACIÓN: Temperatura 12.5°C en CP 1');
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`) VALUES
	(4, '2025-12-11 20:27:28', 'EV_W', 'weather_alert', 'ALERTA METEOROLÓGICA: Temperatura -5°C en CP 1');
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`) VALUES
	(5, '2025-12-11 20:31:07', 'EV_W', 'weather_alert', 'NORMALIZACIÓN: Temperatura 11°C en CP 1');
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`) VALUES
	(6, '2025-12-11 20:39:11', NULL, 'weather_alert', 'ACTUALIZACIÓN: Nueva temperatura 15.88°C en CP 1');
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`) VALUES
	(7, '2025-12-11 20:39:11', NULL, 'weather_alert', 'ACTUALIZACIÓN: Nueva temperatura 12.7°C en CP 2');
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`) VALUES
	(8, '2025-12-11 20:39:11', NULL, 'weather_alert', 'ACTUALIZACIÓN: Nueva temperatura 8.53°C en CP 3');
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`) VALUES
	(9, '2025-12-11 20:39:56', NULL, 'weather_alert', 'NORMALIZACIÓN: Temperatura 15.7°C en CP 1');
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`) VALUES
	(10, '2025-12-11 20:42:48', NULL, 'weather_alert', 'NORMALIZACIÓN: Temperatura 15.7°C en CP 1');
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`) VALUES
	(11, '2025-12-12 10:32:19', 'EV_W', 'weather_alert', 'ALERTA METEOROLÓGICA: Temperatura -10°C en CP 1');
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`) VALUES
	(12, '2025-12-12 10:32:42', 'EV_W', 'weather_alert', 'NORMALIZACIÓN: Temperatura 20°C en CP 1');
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`) VALUES
	(13, '2025-12-12 10:32:54', 'EV_W', 'weather_alert', 'ALERTA METEOROLÓGICA: Temperatura -7°C en CP 1');
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`) VALUES
	(14, '2025-12-12 10:37:46', 'EV_W', 'weather_alert', 'ALERTA METEOROLÓGICA: Temperatura -12°C en CP 1');
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`) VALUES
	(15, '2025-12-12 10:38:05', 'EV_W', 'weather_alert', 'NORMALIZACIÓN: Temperatura 30°C en CP 1');
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`) VALUES
	(16, '2025-12-12 10:38:18', 'EV_W', 'weather_alert', 'ALERTA METEOROLÓGICA: Temperatura -11°C en CP 1');
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`) VALUES
	(17, '2025-12-12 10:38:34', 'EV_W', 'weather_alert', 'NORMALIZACIÓN: Temperatura 15.6°C en CP 1');
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`) VALUES
	(18, '2025-12-12 10:39:03', 'EV_W', 'weather_alert', 'ALERTA METEOROLÓGICA: Temperatura -30°C en CP 1');
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`) VALUES
	(19, '2025-12-12 10:39:15', 'EV_W', 'weather_alert', 'NORMALIZACIÓN: Temperatura 11°C en CP 1');
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`) VALUES
	(20, '2025-12-12 11:32:16', 'EV_W', 'weather_alert', 'ALERTA METEOROLÓGICA: Temperatura -20°C en CP 1');
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`) VALUES
	(21, '2025-12-12 11:32:31', 'EV_W', 'weather_alert', 'NORMALIZACIÓN: Temperatura 25°C en CP 1');

-- Volcando estructura para tabla evcharging.central
CREATE TABLE IF NOT EXISTS `central` (
  `id_central` varchar(10) NOT NULL,
  `ubicacion_central` varchar(255) DEFAULT NULL,
  `email_central` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id_central`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Volcando datos para la tabla evcharging.central: ~1 rows (aproximadamente)
DELETE FROM `central`;
INSERT INTO `central` (`id_central`, `ubicacion_central`, `email_central`) VALUES
	('0039051', 'EPS 4 - Universidad de Alicante', 'sistemasdistribuidos2526ua@gmail.com');

-- Volcando estructura para tabla evcharging.conductor
CREATE TABLE IF NOT EXISTS `conductor` (
  `id_conductor` varchar(10) NOT NULL,
  `nombre` varchar(50) NOT NULL,
  `apellidos` varchar(100) NOT NULL,
  `email_conductor` varchar(50) NOT NULL,
  `telefono_conductor` varchar(16) NOT NULL,
  `dni_conductor` varchar(10) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Volcando datos para la tabla evcharging.conductor: ~16 rows (aproximadamente)
DELETE FROM `conductor`;
INSERT INTO `conductor` (`id_conductor`, `nombre`, `apellidos`, `email_conductor`, `telefono_conductor`, `dni_conductor`) VALUES
	('AAA1', 'Cambio2', 'uno', 'pruebaupdate1@gmail.com', '123456789', '12345678U');
INSERT INTO `conductor` (`id_conductor`, `nombre`, `apellidos`, `email_conductor`, `telefono_conductor`, `dni_conductor`) VALUES
	('AAA2', 'Pedro', 'Rizo Valero', 'pedrosd2526@gmail.com', '642982651', '21381363L');
INSERT INTO `conductor` (`id_conductor`, `nombre`, `apellidos`, `email_conductor`, `telefono_conductor`, `dni_conductor`) VALUES
	('AAA3', 'Raúl', 'Varó López', 'raulsd2526@gmail.com', '680129257', '72942573F');
INSERT INTO `conductor` (`id_conductor`, `nombre`, `apellidos`, `email_conductor`, `telefono_conductor`, `dni_conductor`) VALUES
	('AAA4', 'Carlos', 'García Rodríguez', 'carlosgr2526@gmail.com', '612345678', '51234567A');
INSERT INTO `conductor` (`id_conductor`, `nombre`, `apellidos`, `email_conductor`, `telefono_conductor`, `dni_conductor`) VALUES
	('AAA5', 'María', 'Fernández López', 'mariafl2526@gmail.com', '623456789', '42345678B');
INSERT INTO `conductor` (`id_conductor`, `nombre`, `apellidos`, `email_conductor`, `telefono_conductor`, `dni_conductor`) VALUES
	('AAA6', 'Javier', 'Martínez Sánchez', 'javierms2526@gmail.com', '634567890', '33456789C');
INSERT INTO `conductor` (`id_conductor`, `nombre`, `apellidos`, `email_conductor`, `telefono_conductor`, `dni_conductor`) VALUES
	('AAA7', 'Laura', 'González Pérez', 'lauragp2526@gmail.com', '645678901', '24567890D');
INSERT INTO `conductor` (`id_conductor`, `nombre`, `apellidos`, `email_conductor`, `telefono_conductor`, `dni_conductor`) VALUES
	('AAA8', 'David', 'Rodríguez Martín', 'davidrm2526@gmail.com', '656789012', '15678901E');
INSERT INTO `conductor` (`id_conductor`, `nombre`, `apellidos`, `email_conductor`, `telefono_conductor`, `dni_conductor`) VALUES
	('AAA9', 'Ana', 'López García', 'analg2526@gmail.com', '667890123', '06789012F');
INSERT INTO `conductor` (`id_conductor`, `nombre`, `apellidos`, `email_conductor`, `telefono_conductor`, `dni_conductor`) VALUES
	('AAA10', 'Miguel', 'Sánchez Fernández', 'miguelsf2526@gmail.com', '678901234', '97890123G');
INSERT INTO `conductor` (`id_conductor`, `nombre`, `apellidos`, `email_conductor`, `telefono_conductor`, `dni_conductor`) VALUES
	('AAA11', 'Elena', 'Pérez González', 'elenapg2526@gmail.com', '689012345', '88901234H');
INSERT INTO `conductor` (`id_conductor`, `nombre`, `apellidos`, `email_conductor`, `telefono_conductor`, `dni_conductor`) VALUES
	('AAA12', 'Daniel', 'Ramírez Torres', 'danielrt2526@gmail.com', '690123456', '79012345I');
INSERT INTO `conductor` (`id_conductor`, `nombre`, `apellidos`, `email_conductor`, `telefono_conductor`, `dni_conductor`) VALUES
	('AAA13', 'Sofía', 'Torres Ramírez', 'sofiart2526@gmail.com', '601234567', '60123456J');
INSERT INTO `conductor` (`id_conductor`, `nombre`, `apellidos`, `email_conductor`, `telefono_conductor`, `dni_conductor`) VALUES
	('AAA14', 'Aarón', 'Sáncez Pérez', 'aasp02@gmail.com', '657840932', '23905643L');
INSERT INTO `conductor` (`id_conductor`, `nombre`, `apellidos`, `email_conductor`, `telefono_conductor`, `dni_conductor`) VALUES
	('AAA15', 'David', 'Muñoz Rivera', 'maesomuñrvera@gmail.com', '698234509', '12984587F');
INSERT INTO `conductor` (`id_conductor`, `nombre`, `apellidos`, `email_conductor`, `telefono_conductor`, `dni_conductor`) VALUES
	('AAA16', 'Cambio2', 'uno', 'pruebaupdate1@gmail.com', '123456789', '12345678U');

-- Volcando estructura para tabla evcharging.punto_recarga
CREATE TABLE IF NOT EXISTS `punto_recarga` (
  `id_punto_recarga` int(11) NOT NULL AUTO_INCREMENT,
  `id_central` varchar(10) NOT NULL,
  `ubicacion_punto_recarga` varchar(255) NOT NULL,
  `precio` decimal(8,3) NOT NULL,
  `estado` varchar(20) DEFAULT NULL,
  `temperatura` decimal(4,1) DEFAULT 20.0,
  `ultima_actualizacion` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `activo` tinyint(1) NOT NULL DEFAULT 1,
  `credencial` varchar(255) DEFAULT NULL,
  `tiene_clave_simetrica` tinyint(1) NOT NULL DEFAULT 0,
  PRIMARY KEY (`id_punto_recarga`),
  KEY `fk_punto_recarga_central` (`id_central`),
  CONSTRAINT `fk_punto_recarga_central` FOREIGN KEY (`id_central`) REFERENCES `central` (`id_central`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Volcando datos para la tabla evcharging.punto_recarga: ~3 rows (aproximadamente)
DELETE FROM `punto_recarga`;
INSERT INTO `punto_recarga` (`id_punto_recarga`, `id_central`, `ubicacion_punto_recarga`, `precio`, `estado`, `temperatura`, `ultima_actualizacion`, `activo`, `credencial`, `tiene_clave_simetrica`) VALUES
	(1, '0039051', 'PRUEBA3', 1.150, 'ACTIVADO', 25.0, '2025-12-12 11:06:38', 1, NULL, 0);
INSERT INTO `punto_recarga` (`id_punto_recarga`, `id_central`, `ubicacion_punto_recarga`, `precio`, `estado`, `temperatura`, `ultima_actualizacion`, `activo`, `credencial`, `tiene_clave_simetrica`) VALUES
	(2, '0039051', 'Zona 2 – EPS 4 – Universidad de Alicante', 0.350, 'DESCONECTADO', 12.7, '2025-12-11 19:39:11', 1, NULL, 0);
INSERT INTO `punto_recarga` (`id_punto_recarga`, `id_central`, `ubicacion_punto_recarga`, `precio`, `estado`, `temperatura`, `ultima_actualizacion`, `activo`, `credencial`, `tiene_clave_simetrica`) VALUES
	(3, '0039051', 'Zona 3 – EPS 4 – Universidad de Alicante', 0.350, 'DESCONECTADO', 8.5, '2025-12-11 19:39:11', 1, NULL, 0);

-- Volcando estructura para disparador evcharging.generar_id_conductor
SET @OLDTMP_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_ZERO_IN_DATE,NO_ZERO_DATE,NO_ENGINE_SUBSTITUTION';
DELIMITER //
CREATE TRIGGER generar_id_conductor
BEFORE INSERT ON conductor
FOR EACH ROW
BEGIN
    DECLARE max_numero INT;
    
    -- Encontrar el número máximo actual
    SELECT IFNULL(MAX(CAST(SUBSTRING(id_conductor, 4) AS UNSIGNED)), 0) 
    INTO max_numero 
    FROM conductor;
    
    -- Generar nuevo ID
    SET NEW.id_conductor = CONCAT('AAA', (max_numero + 1));
END//
DELIMITER ;
SET SQL_MODE=@OLDTMP_SQL_MODE;

/*!40103 SET TIME_ZONE=IFNULL(@OLD_TIME_ZONE, 'system') */;
/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IFNULL(@OLD_FOREIGN_KEY_CHECKS, 1) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40111 SET SQL_NOTES=IFNULL(@OLD_SQL_NOTES, 1) */;
