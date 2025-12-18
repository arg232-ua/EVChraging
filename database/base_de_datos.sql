-- --------------------------------------------------------
-- Host:                         127.0.0.1
-- Versión del servidor:         8.0.44 - MySQL Community Server - GPL
-- SO del servidor:              Win64
-- HeidiSQL Versión:             12.12.0.7122
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
CREATE DATABASE IF NOT EXISTS `evcharging` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `evcharging`;

-- Volcando estructura para tabla evcharging.auditoria
CREATE TABLE IF NOT EXISTS `auditoria` (
  `id_auditoria` int NOT NULL AUTO_INCREMENT,
  `fecha_hora` datetime NOT NULL,
  `ip_origen` varchar(45) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `accion` varchar(50) COLLATE utf8mb4_general_ci NOT NULL,
  `descripcion` text COLLATE utf8mb4_general_ci,
  PRIMARY KEY (`id_auditoria`)
) ENGINE=InnoDB AUTO_INCREMENT=35 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Volcando datos para la tabla evcharging.auditoria: ~34 rows (aproximadamente)
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
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`) VALUES
	(22, '2025-12-12 13:29:13', 'EV_W', 'weather_alert', 'ALERTA METEOROLÓGICA: Temperatura -4°C en CP 1');
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`) VALUES
	(23, '2025-12-12 13:30:08', 'EV_W', 'weather_alert', 'NORMALIZACIÓN: Temperatura 8°C en CP 1');
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`) VALUES
	(24, '2025-12-12 13:31:00', 'EV_W', 'weather_alert', 'ALERTA METEOROLÓGICA: Temperatura -4°C en CP 1');
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`) VALUES
	(25, '2025-12-12 13:31:35', 'EV_W', 'weather_alert', 'NORMALIZACIÓN: Temperatura 5°C en CP 1');
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`) VALUES
	(26, '2025-12-12 14:38:33', 'Driver-AAA1', 'login_driver', 'Driver AAA1 se ha logueado correctamente');
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`) VALUES
	(27, '2025-12-12 14:39:22', 'Driver-AAA1', 'solicitud_carga', 'Driver AAA1 solicitando suministro en CP 1');
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`) VALUES
	(28, '2025-12-12 14:39:22', 'CENTRAL', 'suministro_concedido', 'Suministro concedido para Driver AAA1 en CP 1');
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`) VALUES
	(29, '2025-12-12 14:40:42', 'CP-1', 'fin_suministro', 'Fin del suministro del Driver AAA1 en el CP 1');
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`) VALUES
	(30, '2025-12-12 14:48:43', 'Driver-AAA1', 'login_driver', 'Driver AAA1 se ha logueado correctamente');
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`) VALUES
	(31, '2025-12-12 14:49:04', 'Driver-AAA1', 'solicitud_carga', 'Driver AAA1 solicitando suministro en CP 1');
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`) VALUES
	(32, '2025-12-12 14:49:04', 'CENTRAL', 'suministro_concedido', 'Suministro concedido para Driver AAA1 en CP 1');
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`) VALUES
	(33, '2025-12-12 14:49:23', 'CP-1', 'inicio_suministro', 'Driver AAA1 iniciando suministro en CP 1');
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`) VALUES
	(34, '2025-12-12 14:49:41', 'CP-1', 'fin_suministro', 'Fin del suministro del Driver AAA1 en el CP 1');

-- Volcando estructura para tabla evcharging.central
CREATE TABLE IF NOT EXISTS `central` (
  `id_central` varchar(10) COLLATE utf8mb4_general_ci NOT NULL,
  `ubicacion_central` varchar(255) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `email_central` varchar(50) COLLATE utf8mb4_general_ci DEFAULT NULL,
  PRIMARY KEY (`id_central`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Volcando datos para la tabla evcharging.central: ~0 rows (aproximadamente)
DELETE FROM `central`;
INSERT INTO `central` (`id_central`, `ubicacion_central`, `email_central`) VALUES
	('0039051', 'EPS 4 - Universidad de Alicante', 'sistemasdistribuidos2526ua@gmail.com');

-- Volcando estructura para tabla evcharging.conductor
CREATE TABLE IF NOT EXISTS `conductor` (
  `id_conductor` varchar(10) COLLATE utf8mb4_general_ci NOT NULL,
  `nombre` varchar(50) COLLATE utf8mb4_general_ci NOT NULL,
  `apellidos` varchar(100) COLLATE utf8mb4_general_ci NOT NULL,
  `email_conductor` varchar(50) COLLATE utf8mb4_general_ci NOT NULL,
  `telefono_conductor` varchar(16) COLLATE utf8mb4_general_ci NOT NULL,
  `dni_conductor` varchar(10) COLLATE utf8mb4_general_ci NOT NULL,
  `estado` varchar(50) COLLATE utf8mb4_general_ci DEFAULT 'Desconectado'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Volcando datos para la tabla evcharging.conductor: ~16 rows (aproximadamente)
DELETE FROM `conductor`;
INSERT INTO `conductor` (`id_conductor`, `nombre`, `apellidos`, `email_conductor`, `telefono_conductor`, `dni_conductor`, `estado`) VALUES
	('AAA1', 'Cambio2', 'uno', 'pruebaupdate1@gmail.com', '123456789', '12345678U', 'Desconectado');
INSERT INTO `conductor` (`id_conductor`, `nombre`, `apellidos`, `email_conductor`, `telefono_conductor`, `dni_conductor`, `estado`) VALUES
	('AAA2', 'Pedro', 'Rizo Valero', 'pedrosd2526@gmail.com', '642982651', '21381363L', 'Desconectado');
INSERT INTO `conductor` (`id_conductor`, `nombre`, `apellidos`, `email_conductor`, `telefono_conductor`, `dni_conductor`, `estado`) VALUES
	('AAA3', 'Raúl', 'Varó López', 'raulsd2526@gmail.com', '680129257', '72942573F', 'Desconectado');
INSERT INTO `conductor` (`id_conductor`, `nombre`, `apellidos`, `email_conductor`, `telefono_conductor`, `dni_conductor`, `estado`) VALUES
	('AAA4', 'Carlos', 'García Rodríguez', 'carlosgr2526@gmail.com', '612345678', '51234567A', 'Desconectado');
INSERT INTO `conductor` (`id_conductor`, `nombre`, `apellidos`, `email_conductor`, `telefono_conductor`, `dni_conductor`, `estado`) VALUES
	('AAA5', 'María', 'Fernández López', 'mariafl2526@gmail.com', '623456789', '42345678B', 'Desconectado');
INSERT INTO `conductor` (`id_conductor`, `nombre`, `apellidos`, `email_conductor`, `telefono_conductor`, `dni_conductor`, `estado`) VALUES
	('AAA6', 'Javier', 'Martínez Sánchez', 'javierms2526@gmail.com', '634567890', '33456789C', 'Desconectado');
INSERT INTO `conductor` (`id_conductor`, `nombre`, `apellidos`, `email_conductor`, `telefono_conductor`, `dni_conductor`, `estado`) VALUES
	('AAA7', 'Laura', 'González Pérez', 'lauragp2526@gmail.com', '645678901', '24567890D', 'Desconectado');
INSERT INTO `conductor` (`id_conductor`, `nombre`, `apellidos`, `email_conductor`, `telefono_conductor`, `dni_conductor`, `estado`) VALUES
	('AAA8', 'David', 'Rodríguez Martín', 'davidrm2526@gmail.com', '656789012', '15678901E', 'Desconectado');
INSERT INTO `conductor` (`id_conductor`, `nombre`, `apellidos`, `email_conductor`, `telefono_conductor`, `dni_conductor`, `estado`) VALUES
	('AAA9', 'Ana', 'López García', 'analg2526@gmail.com', '667890123', '06789012F', 'Desconectado');
INSERT INTO `conductor` (`id_conductor`, `nombre`, `apellidos`, `email_conductor`, `telefono_conductor`, `dni_conductor`, `estado`) VALUES
	('AAA10', 'Miguel', 'Sánchez Fernández', 'miguelsf2526@gmail.com', '678901234', '97890123G', 'Desconectado');
INSERT INTO `conductor` (`id_conductor`, `nombre`, `apellidos`, `email_conductor`, `telefono_conductor`, `dni_conductor`, `estado`) VALUES
	('AAA11', 'Elena', 'Pérez González', 'elenapg2526@gmail.com', '689012345', '88901234H', 'Desconectado');
INSERT INTO `conductor` (`id_conductor`, `nombre`, `apellidos`, `email_conductor`, `telefono_conductor`, `dni_conductor`, `estado`) VALUES
	('AAA12', 'Daniel', 'Ramírez Torres', 'danielrt2526@gmail.com', '690123456', '79012345I', 'Desconectado');
INSERT INTO `conductor` (`id_conductor`, `nombre`, `apellidos`, `email_conductor`, `telefono_conductor`, `dni_conductor`, `estado`) VALUES
	('AAA13', 'Sofía', 'Torres Ramírez', 'sofiart2526@gmail.com', '601234567', '60123456J', 'Desconectado');
INSERT INTO `conductor` (`id_conductor`, `nombre`, `apellidos`, `email_conductor`, `telefono_conductor`, `dni_conductor`, `estado`) VALUES
	('AAA14', 'Aarón', 'Sáncez Pérez', 'aasp02@gmail.com', '657840932', '23905643L', 'Desconectado');
INSERT INTO `conductor` (`id_conductor`, `nombre`, `apellidos`, `email_conductor`, `telefono_conductor`, `dni_conductor`, `estado`) VALUES
	('AAA15', 'David', 'Muñoz Rivera', 'maesomuñrvera@gmail.com', '698234509', '12984587F', 'Desconectado');
INSERT INTO `conductor` (`id_conductor`, `nombre`, `apellidos`, `email_conductor`, `telefono_conductor`, `dni_conductor`, `estado`) VALUES
	('AAA16', 'Cambio2', 'uno', 'pruebaupdate1@gmail.com', '123456789', '12345678U', 'Desconectado');

-- Volcando estructura para tabla evcharging.punto_recarga
CREATE TABLE IF NOT EXISTS `punto_recarga` (
  `id_punto_recarga` int NOT NULL AUTO_INCREMENT,
  `id_central` varchar(10) COLLATE utf8mb4_general_ci NOT NULL,
  `ubicacion_punto_recarga` varchar(255) COLLATE utf8mb4_general_ci NOT NULL,
  `precio` decimal(8,3) NOT NULL,
  `estado` varchar(20) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `temperatura` decimal(4,1) DEFAULT '20.0',
  `ultima_actualizacion` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `activo` tinyint(1) NOT NULL DEFAULT '1',
  `credencial` varchar(255) COLLATE utf8mb4_general_ci DEFAULT NULL,
  `tiene_clave_simetrica` tinyint(1) NOT NULL DEFAULT '0',
  `cp_logico` int DEFAULT NULL,
  PRIMARY KEY (`id_punto_recarga`),
  UNIQUE KEY `cp_logico` (`cp_logico`),
  KEY `fk_punto_recarga_central` (`id_central`),
  CONSTRAINT `fk_punto_recarga_central` FOREIGN KEY (`id_central`) REFERENCES `central` (`id_central`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Volcando datos para la tabla evcharging.punto_recarga: ~9 rows (aproximadamente)
DELETE FROM `punto_recarga`;
INSERT INTO `punto_recarga` (`id_punto_recarga`, `id_central`, `ubicacion_punto_recarga`, `precio`, `estado`, `temperatura`, `ultima_actualizacion`, `activo`, `credencial`, `tiene_clave_simetrica`, `cp_logico`) VALUES
	(1, '0039051', 'PRUEBA3', 1.150, 'DESCONECTADO', 5.0, '2025-12-13 15:43:41', 1, NULL, 0, 1);
INSERT INTO `punto_recarga` (`id_punto_recarga`, `id_central`, `ubicacion_punto_recarga`, `precio`, `estado`, `temperatura`, `ultima_actualizacion`, `activo`, `credencial`, `tiene_clave_simetrica`, `cp_logico`) VALUES
	(2, '0039051', 'Zona 2 – EPS 4 – Universidad de Alicante', 0.350, 'DESCONECTADO', 12.7, '2025-12-13 16:16:54', 1, '21def710ca112b069c79515772b24cdc070cd0ddc553e1f3', 0, 2);
INSERT INTO `punto_recarga` (`id_punto_recarga`, `id_central`, `ubicacion_punto_recarga`, `precio`, `estado`, `temperatura`, `ultima_actualizacion`, `activo`, `credencial`, `tiene_clave_simetrica`, `cp_logico`) VALUES
	(3, '0039051', 'Zona 3 – EPS 4 – Universidad de Alicante', 0.350, 'DESCONECTADO', 8.5, '2025-12-13 16:29:33', 1, '58f94002581bee22a141a81376caa2c2568162eb6b35a166', 0, 3);
INSERT INTO `punto_recarga` (`id_punto_recarga`, `id_central`, `ubicacion_punto_recarga`, `precio`, `estado`, `temperatura`, `ultima_actualizacion`, `activo`, `credencial`, `tiene_clave_simetrica`, `cp_logico`) VALUES
	(4, '0039051', 'CP 1 – EPS', 0.350, 'DESCONECTADO', 20.0, '2025-12-13 12:49:49', 1, 'b98c1e64458567ed414b974ce08f3b94b50d08d2549f2c17', 0, NULL);
INSERT INTO `punto_recarga` (`id_punto_recarga`, `id_central`, `ubicacion_punto_recarga`, `precio`, `estado`, `temperatura`, `ultima_actualizacion`, `activo`, `credencial`, `tiene_clave_simetrica`, `cp_logico`) VALUES
	(5, '0039051', 'CP 1 – EPS', 0.350, 'DESCONECTADO', 20.0, '2025-12-13 15:30:07', 1, 'fa8915f6cea0c0c25c5b2515b5b020508a7c5d3288d6374e', 0, NULL);
INSERT INTO `punto_recarga` (`id_punto_recarga`, `id_central`, `ubicacion_punto_recarga`, `precio`, `estado`, `temperatura`, `ultima_actualizacion`, `activo`, `credencial`, `tiene_clave_simetrica`, `cp_logico`) VALUES
	(6, '0039051', 'CP 2 – EPS', 0.350, 'DESCONECTADO', 20.0, '2025-12-13 16:08:56', 1, '134d81daa1fe8139093ecd1759c98bbee1e2c044e2303214', 0, NULL);
INSERT INTO `punto_recarga` (`id_punto_recarga`, `id_central`, `ubicacion_punto_recarga`, `precio`, `estado`, `temperatura`, `ultima_actualizacion`, `activo`, `credencial`, `tiene_clave_simetrica`, `cp_logico`) VALUES
	(7, '0039051', 'CP 7 – EPS', 0.350, 'DESCONECTADO', 20.0, '2025-12-13 16:30:18', 1, 'ecb7f2b7f5bb4a96e4b66ee8362a2b5b144d93a59b9a8557', 0, 7);
INSERT INTO `punto_recarga` (`id_punto_recarga`, `id_central`, `ubicacion_punto_recarga`, `precio`, `estado`, `temperatura`, `ultima_actualizacion`, `activo`, `credencial`, `tiene_clave_simetrica`, `cp_logico`) VALUES
	(8, '0039051', 'CP 8 – EPS', 0.350, 'DESCONECTADO', 20.0, '2025-12-13 16:36:04', 1, '71e97c9c6bf08f63ca02dce1ea0549f1fb29cce9fdd3ff4a', 0, 8);
INSERT INTO `punto_recarga` (`id_punto_recarga`, `id_central`, `ubicacion_punto_recarga`, `precio`, `estado`, `temperatura`, `ultima_actualizacion`, `activo`, `credencial`, `tiene_clave_simetrica`, `cp_logico`) VALUES
	(9, '0039051', 'CP 9 – EPS', 0.350, 'DESCONECTADO', 20.0, '2025-12-13 16:40:44', 1, '6e95067f3bcbd93ce0602401aad3de278614a53cbd94cadf', 0, 9);

/*!40103 SET TIME_ZONE=IFNULL(@OLD_TIME_ZONE, 'system') */;
/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IFNULL(@OLD_FOREIGN_KEY_CHECKS, 1) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40111 SET SQL_NOTES=IFNULL(@OLD_SQL_NOTES, 1) */;
