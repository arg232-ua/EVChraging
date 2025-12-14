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
  `alerta_activa` tinyint(1) DEFAULT 0,
  PRIMARY KEY (`id_auditoria`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Volcando datos para la tabla evcharging.auditoria: ~164 rows (aproximadamente)
DELETE FROM `auditoria`;
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(1, '2025-12-11 12:38:09', '::1', 'weather_alert', 'CP 1: Temperatura -10°C - ALERTA POR FRÍO', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(2, '2025-12-11 12:39:12', '::1', 'weather_alert', 'CP 1: Temperatura 17°C - ALERTA FINALIZADA', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(3, '2025-12-11 20:25:15', 'EV_W', 'weather_alert', 'NORMALIZACIÓN: Temperatura 12.5°C en CP 1', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(4, '2025-12-11 20:27:28', 'EV_W', 'weather_alert', 'ALERTA METEOROLÓGICA: Temperatura -5°C en CP 1', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(5, '2025-12-11 20:31:07', 'EV_W', 'weather_alert', 'NORMALIZACIÓN: Temperatura 11°C en CP 1', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(6, '2025-12-11 20:39:11', NULL, 'weather_alert', 'ACTUALIZACIÓN: Nueva temperatura 15.88°C en CP 1', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(7, '2025-12-11 20:39:11', NULL, 'weather_alert', 'ACTUALIZACIÓN: Nueva temperatura 12.7°C en CP 2', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(8, '2025-12-11 20:39:11', NULL, 'weather_alert', 'ACTUALIZACIÓN: Nueva temperatura 8.53°C en CP 3', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(9, '2025-12-11 20:39:56', NULL, 'weather_alert', 'NORMALIZACIÓN: Temperatura 15.7°C en CP 1', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(10, '2025-12-11 20:42:48', NULL, 'weather_alert', 'NORMALIZACIÓN: Temperatura 15.7°C en CP 1', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(11, '2025-12-12 10:32:19', 'EV_W', 'weather_alert', 'ALERTA METEOROLÓGICA: Temperatura -10°C en CP 1', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(12, '2025-12-12 10:32:42', 'EV_W', 'weather_alert', 'NORMALIZACIÓN: Temperatura 20°C en CP 1', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(13, '2025-12-12 10:32:54', 'EV_W', 'weather_alert', 'ALERTA METEOROLÓGICA: Temperatura -7°C en CP 1', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(14, '2025-12-12 10:37:46', 'EV_W', 'weather_alert', 'ALERTA METEOROLÓGICA: Temperatura -12°C en CP 1', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(15, '2025-12-12 10:38:05', 'EV_W', 'weather_alert', 'NORMALIZACIÓN: Temperatura 30°C en CP 1', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(16, '2025-12-12 10:38:18', 'EV_W', 'weather_alert', 'ALERTA METEOROLÓGICA: Temperatura -11°C en CP 1', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(17, '2025-12-12 10:38:34', 'EV_W', 'weather_alert', 'NORMALIZACIÓN: Temperatura 15.6°C en CP 1', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(18, '2025-12-12 10:39:03', 'EV_W', 'weather_alert', 'ALERTA METEOROLÓGICA: Temperatura -30°C en CP 1', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(19, '2025-12-12 10:39:15', 'EV_W', 'weather_alert', 'NORMALIZACIÓN: Temperatura 11°C en CP 1', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(20, '2025-12-12 11:32:16', 'EV_W', 'weather_alert', 'ALERTA METEOROLÓGICA: Temperatura -20°C en CP 1', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(21, '2025-12-12 11:32:31', 'EV_W', 'weather_alert', 'NORMALIZACIÓN: Temperatura 25°C en CP 1', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(22, '2025-12-12 13:29:13', 'EV_W', 'weather_alert', 'ALERTA METEOROLÓGICA: Temperatura -4°C en CP 1', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(23, '2025-12-12 13:30:08', 'EV_W', 'weather_alert', 'NORMALIZACIÓN: Temperatura 8°C en CP 1', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(24, '2025-12-12 13:31:00', 'EV_W', 'weather_alert', 'ALERTA METEOROLÓGICA: Temperatura -4°C en CP 1', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(25, '2025-12-12 13:31:35', 'EV_W', 'weather_alert', 'NORMALIZACIÓN: Temperatura 5°C en CP 1', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(26, '2025-12-12 14:38:33', 'Driver-AAA1', 'login_driver', 'Driver AAA1 se ha logueado correctamente', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(27, '2025-12-12 14:39:22', 'Driver-AAA1', 'solicitud_carga', 'Driver AAA1 solicitando suministro en CP 1', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(28, '2025-12-12 14:39:22', 'CENTRAL', 'suministro_concedido', 'Suministro concedido para Driver AAA1 en CP 1', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(29, '2025-12-12 14:40:42', 'CP-1', 'fin_suministro', 'Fin del suministro del Driver AAA1 en el CP 1', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(30, '2025-12-12 14:48:43', 'Driver-AAA1', 'login_driver', 'Driver AAA1 se ha logueado correctamente', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(31, '2025-12-12 14:49:04', 'Driver-AAA1', 'solicitud_carga', 'Driver AAA1 solicitando suministro en CP 1', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(32, '2025-12-12 14:49:04', 'CENTRAL', 'suministro_concedido', 'Suministro concedido para Driver AAA1 en CP 1', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(33, '2025-12-12 14:49:23', 'CP-1', 'inicio_suministro', 'Driver AAA1 iniciando suministro en CP 1', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(34, '2025-12-12 14:49:41', 'CP-1', 'fin_suministro', 'Fin del suministro del Driver AAA1 en el CP 1', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(35, '2025-12-14 14:51:59', 'Driver-AAA1', 'login_driver', 'Driver AAA1 se ha logueado correctamente', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(36, '2025-12-14 14:52:17', 'Driver-AAA1', 'solicitud_carga', 'Driver AAA1 solicitando suministro en CP 1', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(37, '2025-12-14 14:52:17', 'CENTRAL', 'suministro_concedido', 'Suministro concedido para Driver AAA1 en CP 1', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(38, '2025-12-14 14:52:36', 'CP-1', 'inicio_suministro', 'Driver AAA1 iniciando suministro en CP 1', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(39, '2025-12-14 14:53:12', 'CP-1', 'fin_suministro', 'Fin del suministro del Driver AAA1 en el CP 1', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(40, '2025-12-14 14:54:01', 'EV_W', 'weather_alert', 'ALERTA METEOROLÓGICA: Temperatura -10°C en CP 1', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(41, '2025-12-14 14:54:43', 'EV_W', 'weather_alert', 'NORMALIZACIÓN: Temperatura 11°C en CP 1', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(42, '2025-12-14 15:01:39', 'Driver-AAA1', 'login_driver', 'Driver AAA1 se ha logueado correctamente', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(43, '2025-12-14 15:02:52', 'EV_W', 'weather_alert', 'ALERTA METEOROLÓGICA: Temperatura -3°C en CP 1', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(44, '2025-12-14 15:03:19', 'EV_W', 'weather_alert', 'NORMALIZACIÓN: Temperatura 11°C en CP 1', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(45, '2025-12-14 15:04:19', 'Frontend', 'config_update', 'Ciudad cambiada para CP 1: Alicante,ES → Madrid,ES', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(46, '2025-12-14 15:04:40', 'Frontend', 'config_update', 'Ciudad cambiada para CP 1: Madrid,ES → Alicante,ES', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(47, '2025-12-14 15:06:34', 'Frontend', 'config_update', 'Ciudad cambiada para CP 1: Alicante,ES → Barcelona,ES', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(48, '2025-12-14 18:08:15', 'EV_W', 'weather_alert', 'ACTUALIZACIÓN: Nueva temperatura 14.06°C en CP 1', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(49, '2025-12-14 18:08:15', 'EV_W', 'weather_alert', 'ACTUALIZACIÓN: Nueva temperatura 15.65°C en CP 2', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(50, '2025-12-14 18:08:15', 'EV_W', 'weather_alert', 'ACTUALIZACIÓN: Nueva temperatura 10.85°C en CP 3', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(51, '2025-12-14 18:09:39', 'EV_W', 'weather_alert', 'ALERTA METEOROLÓGICA: Temperatura -10°C en CP 1', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(52, '2025-12-14 18:09:57', 'EV_W', 'weather_alert', 'NORMALIZACIÓN: Temperatura 11°C en CP 1', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(53, '2025-12-14 18:10:27', 'Frontend', 'config_update', 'Ciudad cambiada para CP 1: Barcelona,ES → Barcelona,ES', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(54, '2025-12-14 18:10:50', 'Frontend', 'config_update', 'Ciudad cambiada para CP 1: Barcelona,ES → Alicante,ES', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(55, '2025-12-14 18:11:37', 'EV_W', 'weather_alert', 'ALERTA METEOROLÓGICA: Temperatura -10°C en CP 1', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(56, '2025-12-14 18:12:26', 'EV_W', 'weather_alert', 'ACTUALIZACIÓN: Nueva temperatura 17.49°C en CP 1', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(57, '2025-12-14 18:12:26', 'EV_W', 'weather_alert', 'ACTUALIZACIÓN: Nueva temperatura 15.7°C en CP 2', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(58, '2025-12-14 18:12:26', 'EV_W', 'weather_alert', 'ACTUALIZACIÓN: Nueva temperatura 10.7°C en CP 3', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(59, '2025-12-14 18:12:45', 'EV_W', 'weather_alert', 'NORMALIZACIÓN: Temperatura 17.49°C en CP 1', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(60, '2025-12-14 18:13:02', 'EV_W', 'weather_alert', 'ACTUALIZACIÓN: Nueva temperatura 17.49°C en CP 1', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(61, '2025-12-14 18:13:02', 'EV_W', 'weather_alert', 'ACTUALIZACIÓN: Nueva temperatura 15.7°C en CP 2', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(62, '2025-12-14 18:13:02', 'EV_W', 'weather_alert', 'ACTUALIZACIÓN: Nueva temperatura 10.7°C en CP 3', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(63, '2025-12-14 18:13:37', 'Frontend', 'config_update', 'Ciudad cambiada para CP 1: Alicante,ES → Barcelona,ES', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(64, '2025-12-14 18:37:25', 'EV_W', 'weather_alert', 'ACTUALIZACIÓN: Nueva temperatura 14.27°C en CP 1', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(65, '2025-12-14 18:37:25', 'EV_W', 'weather_alert', 'ACTUALIZACIÓN: Nueva temperatura 15.8°C en CP 2', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(66, '2025-12-14 18:37:25', 'EV_W', 'weather_alert', 'ACTUALIZACIÓN: Nueva temperatura 10.68°C en CP 3', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(67, '2025-12-14 18:38:09', 'Frontend', 'config_update', 'Ciudad cambiada para CP 1: Barcelona,ES → Alicante,ES', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(68, '2025-12-14 18:47:32', 'EV_W', 'weather_alert', 'ACTUALIZACIÓN: Nueva temperatura 17.65°C en CP 1', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(69, '2025-12-14 18:47:32', 'EV_W', 'weather_alert', 'ACTUALIZACIÓN: Nueva temperatura 15.8°C en CP 2', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(70, '2025-12-14 18:47:32', 'EV_W', 'weather_alert', 'ACTUALIZACIÓN: Nueva temperatura 10.74°C en CP 3', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(71, '2025-12-14 18:47:55', 'Frontend', 'config_update', 'Ciudad cambiada para CP 1: Alicante,ES → Barcelona,ES', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(72, '2025-12-14 18:48:11', 'EV_W', 'weather_alert', 'ACTUALIZACIÓN: Nueva temperatura 14.26°C en CP 1', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(73, '2025-12-14 18:48:50', 'Frontend', 'config_update', 'Ciudad cambiada para CP 1: Barcelona,ES → Alicante,ES', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(74, '2025-12-14 18:48:54', 'EV_W', 'weather_alert', 'ACTUALIZACIÓN: Nueva temperatura 17.65°C en CP 1', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(75, '2025-12-14 18:50:05', 'Frontend', 'config_update', 'Ciudad cambiada para CP 1: Alicante,ES → Suiza,ES', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(76, '2025-12-14 18:51:02', 'Frontend', 'config_update', 'Ciudad cambiada para CP 1: Suiza,ES → London,UK', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(77, '2025-12-14 18:51:02', 'EV_W', 'weather_alert', 'ACTUALIZACIÓN: Nueva temperatura 9.58°C en CP 1', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(78, '2025-12-14 18:51:24', 'Frontend', 'config_update', 'Ciudad cambiada para CP 1: London,UK → Alicante,ES', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(79, '2025-12-14 18:51:24', 'EV_W', 'weather_alert', 'ACTUALIZACIÓN: Nueva temperatura 17.65°C en CP 1', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(80, '2025-12-14 18:51:32', 'Frontend', 'config_update', 'Ciudad cambiada para CP 1: Alicante,ES → Barcelona,ES', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(81, '2025-12-14 18:51:45', 'EV_W', 'weather_alert', 'ACTUALIZACIÓN: Nueva temperatura 14.26°C en CP 1', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(82, '2025-12-14 18:52:57', 'Driver-AAA1', 'login_driver', 'Driver AAA1 se ha logueado correctamente', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(83, '2025-12-14 18:53:47', 'Frontend', 'config_update', 'Ciudad cambiada para CP 1: Barcelona,ES → London,UK', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(84, '2025-12-14 18:53:54', 'EV_W', 'weather_alert', 'ACTUALIZACIÓN: Nueva temperatura 9.58°C en CP 1', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(85, '2025-12-14 18:54:11', 'Driver-AAA1', 'solicitud_carga', 'Driver AAA1 solicitando suministro en CP 1', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(86, '2025-12-14 18:54:12', 'CENTRAL', 'suministro_concedido', 'Suministro concedido para Driver AAA1 en CP 1', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(87, '2025-12-14 18:55:58', 'CP-1', 'inicio_suministro', 'Driver AAA1 iniciando suministro en CP 1', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(88, '2025-12-14 18:56:15', 'CP-1', 'fin_suministro', 'Fin del suministro del Driver AAA1 en el CP 1', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(89, '2025-12-14 18:56:33', 'Frontend', 'config_update', 'Ciudad cambiada para CP 1: London,UK → Indianapolis,US', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(90, '2025-12-14 18:56:45', 'EV_W', 'weather_alert', 'ACTUALIZACIÓN: Nueva temperatura -14.31°C en CP 1', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(91, '2025-12-14 18:56:45', 'EV_W', 'weather_alert', 'ALERTA METEOROLÓGICA: Temperatura -14.31°C en CP 1', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(92, '2025-12-14 18:57:23', 'Driver-AAA1', 'solicitud_carga', 'Driver AAA1 solicitando suministro en CP 1', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(93, '2025-12-14 18:57:23', 'CENTRAL', 'suministro_concedido', 'Suministro concedido para Driver AAA1 en CP 1', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(94, '2025-12-14 18:58:58', 'CP-1', 'inicio_suministro', 'Driver AAA1 iniciando suministro en CP 1', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(95, '2025-12-14 18:59:04', 'CP-1', 'fin_suministro', 'Fin del suministro del Driver AAA1 en el CP 1', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(96, '2025-12-14 19:06:50', 'EV_W', 'weather_alert', 'ACTUALIZACIÓN: Nueva temperatura -13.78°C en CP 1', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(97, '2025-12-14 19:09:23', 'EV_W', 'weather_alert', 'ACTUALIZACIÓN: Nueva temperatura -13.78°C en CP 1', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(98, '2025-12-14 19:09:23', 'EV_W', 'weather_alert', 'ALERTA METEOROLÓGICA: Temperatura -13.78°C en CP 1', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(99, '2025-12-14 19:09:23', 'EV_W', 'weather_alert', 'ACTUALIZACIÓN: Nueva temperatura 15.57°C en CP 2', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(100, '2025-12-14 19:09:23', 'EV_W', 'weather_alert', 'ACTUALIZACIÓN: Nueva temperatura 10.57°C en CP 3', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(101, '2025-12-14 19:09:28', 'Driver-AAA1', 'login_driver', 'Driver AAA1 se ha logueado correctamente', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(102, '2025-12-14 19:09:38', 'Driver-AAA1', 'solicitud_carga', 'Driver AAA1 solicitando suministro en CP 1', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(103, '2025-12-14 19:09:38', 'CENTRAL', 'carga_denegada', 'Solicitud de carga denegada para el Driver AAA1 en CP 1', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(104, '2025-12-14 19:09:55', 'Driver-AAA1', 'solicitud_carga', 'Driver AAA1 solicitando suministro en CP 1', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(105, '2025-12-14 19:09:55', 'CENTRAL', 'carga_denegada', 'Solicitud de carga denegada para el Driver AAA1 en CP 1', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(106, '2025-12-14 19:10:12', 'Frontend', 'config_update', 'Ciudad cambiada para CP 1: Indianapolis,US → Alicante,ES', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(107, '2025-12-14 19:10:23', 'EV_W', 'weather_alert', 'ACTUALIZACIÓN: Nueva temperatura 17.65°C en CP 1', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(108, '2025-12-14 19:10:23', 'EV_W', 'weather_alert', 'NORMALIZACIÓN: Temperatura 17.65°C en CP 1', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(109, '2025-12-14 19:10:44', 'Driver-AAA1', 'solicitud_carga', 'Driver AAA1 solicitando suministro en CP 1', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(110, '2025-12-14 19:10:44', 'CENTRAL', 'carga_denegada', 'Solicitud de carga denegada para el Driver AAA1 en CP 1', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(111, '2025-12-14 19:10:47', 'Driver-AAA1', 'solicitud_carga', 'Driver AAA1 solicitando suministro en CP 1', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(112, '2025-12-14 19:10:47', 'CENTRAL', 'carga_denegada', 'Solicitud de carga denegada para el Driver AAA1 en CP 1', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(113, '2025-12-14 19:11:21', 'Driver-AAA1', 'solicitud_carga', 'Driver AAA1 solicitando suministro en CP 1', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(114, '2025-12-14 19:11:21', 'CENTRAL', 'carga_denegada', 'Solicitud de carga denegada para el Driver AAA1 en CP 1', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(115, '2025-12-14 19:15:03', 'Driver-AAA1', 'login_driver', 'Driver AAA1 se ha logueado correctamente', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(116, '2025-12-14 19:15:07', 'EV_W', 'weather_alert', 'ACTUALIZACIÓN: Nueva temperatura 17.65°C en CP 1', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(117, '2025-12-14 19:15:07', 'EV_W', 'weather_alert', 'ACTUALIZACIÓN: Nueva temperatura 15.57°C en CP 2', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(118, '2025-12-14 19:15:07', 'EV_W', 'weather_alert', 'ACTUALIZACIÓN: Nueva temperatura 10.6°C en CP 3', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(119, '2025-12-14 19:15:48', 'Frontend', 'config_update', 'Ciudad cambiada para CP 1: Alicante,ES → Indianapolis,US', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(120, '2025-12-14 19:16:07', 'EV_W', 'weather_alert', 'ACTUALIZACIÓN: Nueva temperatura -13.78°C en CP 1', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(121, '2025-12-14 19:16:07', 'EV_W', 'weather_alert', 'ALERTA METEOROLÓGICA: Temperatura -13.78°C en CP 1', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(122, '2025-12-14 19:16:36', 'Driver-AAA1', 'solicitud_carga', 'Driver AAA1 solicitando suministro en CP 1', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(123, '2025-12-14 19:16:36', 'CENTRAL', 'carga_denegada', 'Solicitud de carga denegada para el Driver AAA1 en CP 1 - Alerta meteorológica (-13.8°C)', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(124, '2025-12-14 19:16:38', 'Driver-AAA1', 'solicitud_carga', 'Driver AAA1 solicitando suministro en CP 1', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(125, '2025-12-14 19:16:38', 'CENTRAL', 'carga_denegada', 'Solicitud de carga denegada para el Driver AAA1 en CP 1 - Alerta meteorológica (-13.8°C)', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(126, '2025-12-14 19:16:54', 'Frontend', 'config_update', 'Ciudad cambiada para CP 1: Indianapolis,US → Alicante,ES', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(127, '2025-12-14 19:17:12', 'EV_W', 'weather_alert', 'ACTUALIZACIÓN: Nueva temperatura 17.5°C en CP 1', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(128, '2025-12-14 19:17:12', 'EV_W', 'weather_alert', 'NORMALIZACIÓN: Temperatura 17.5°C en CP 1', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(129, '2025-12-14 19:17:43', 'Driver-AAA1', 'solicitud_carga', 'Driver AAA1 solicitando suministro en CP 1', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(130, '2025-12-14 19:17:43', 'CENTRAL', 'suministro_concedido', 'Suministro concedido para Driver AAA1 en CP 1', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(131, '2025-12-14 19:18:06', 'CP-1', 'inicio_suministro', 'Driver AAA1 iniciando suministro en CP 1', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(132, '2025-12-14 19:18:22', 'CP-1', 'fin_suministro', 'Fin del suministro del Driver AAA1 en el CP 1', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(133, '2025-12-14 19:18:36', 'Frontend', 'config_update', 'Ciudad cambiada para CP 1: Alicante,ES → Indianapolis,US', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(134, '2025-12-14 19:18:39', 'EV_W', 'weather_alert', 'ACTUALIZACIÓN: Nueva temperatura -13.98°C en CP 1', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(135, '2025-12-14 19:18:39', 'EV_W', 'weather_alert', 'ALERTA METEOROLÓGICA: Temperatura -13.98°C en CP 1', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(136, '2025-12-14 19:18:58', 'Driver-AAA1', 'solicitud_carga', 'Driver AAA1 solicitando suministro en CP 1', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(137, '2025-12-14 19:18:58', 'CENTRAL', 'carga_denegada', 'Solicitud de carga denegada para el Driver AAA1 en CP 1 - Alerta meteorológica (-14.0°C)', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(138, '2025-12-14 19:19:00', 'Driver-AAA1', 'solicitud_carga', 'Driver AAA1 solicitando suministro en CP 1', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(139, '2025-12-14 19:19:00', 'CENTRAL', 'carga_denegada', 'Solicitud de carga denegada para el Driver AAA1 en CP 1 - Alerta meteorológica (-14.0°C)', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(140, '2025-12-14 19:19:16', 'Frontend', 'config_update', 'Ciudad cambiada para CP 1: Indianapolis,US → Alicante,ES', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(141, '2025-12-14 19:19:23', 'EV_W', 'weather_alert', 'ACTUALIZACIÓN: Nueva temperatura 17.5°C en CP 1', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(142, '2025-12-14 19:19:23', 'EV_W', 'weather_alert', 'NORMALIZACIÓN: Temperatura 17.5°C en CP 1', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(143, '2025-12-14 19:34:06', 'EV_W', 'weather_alert', 'ACTUALIZACIÓN: Nueva temperatura 17.5°C en CP 1', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(144, '2025-12-14 19:34:06', 'EV_W', 'weather_alert', 'ACTUALIZACIÓN: Nueva temperatura 15.61°C en CP 2', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(145, '2025-12-14 19:34:06', 'EV_W', 'weather_alert', 'ACTUALIZACIÓN: Nueva temperatura 10.36°C en CP 3', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(146, '2025-12-14 19:34:09', 'Driver-AAA1', 'login_driver', 'Driver AAA1 se ha logueado correctamente', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(147, '2025-12-14 19:34:37', 'Driver-AAA1', 'solicitud_carga', 'Driver AAA1 solicitando suministro en CP 1', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(148, '2025-12-14 19:34:37', 'CENTRAL', 'suministro_concedido', 'Suministro concedido para Driver AAA1 en CP 1', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(149, '2025-12-14 19:34:53', 'CP-1', 'inicio_suministro', 'Driver AAA1 iniciando suministro en CP 1', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(150, '2025-12-14 19:35:06', 'CP-1', 'fin_suministro', 'Fin del suministro del Driver AAA1 en el CP 1', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(151, '2025-12-14 19:35:21', 'Frontend', 'config_update', 'Ciudad cambiada para CP 1: Alicante,ES → Indianapolis,US', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(152, '2025-12-14 19:35:29', 'EV_W', 'weather_alert', 'ACTUALIZACIÓN: Nueva temperatura -13.37°C en CP 1', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(153, '2025-12-14 19:35:29', 'EV_W', 'weather_alert', 'ALERTA METEOROLÓGICA: Temperatura -13.37°C en CP 1', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(154, '2025-12-14 19:35:54', 'Driver-AAA1', 'solicitud_carga', 'Driver AAA1 solicitando suministro en CP 1', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(155, '2025-12-14 19:35:54', 'CENTRAL', 'carga_denegada', 'Solicitud de carga denegada para el Driver AAA1 en CP 1 - Alerta meteorológica (-13.4°C)', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(156, '2025-12-14 19:35:56', 'Driver-AAA1', 'solicitud_carga', 'Driver AAA1 solicitando suministro en CP 1', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(157, '2025-12-14 19:35:56', 'CENTRAL', 'carga_denegada', 'Solicitud de carga denegada para el Driver AAA1 en CP 1 - Alerta meteorológica (-13.4°C)', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(158, '2025-12-14 19:36:15', 'Frontend', 'config_update', 'Ciudad cambiada para CP 1: Indianapolis,US → Alicante,ES', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(159, '2025-12-14 19:36:34', 'EV_W', 'weather_alert', 'ACTUALIZACIÓN: Nueva temperatura 17.5°C en CP 1', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(160, '2025-12-14 19:36:34', 'EV_W', 'weather_alert', 'NORMALIZACIÓN: Temperatura 17.5°C en CP 1', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(161, '2025-12-14 19:36:47', 'Driver-AAA1', 'solicitud_carga', 'Driver AAA1 solicitando suministro en CP 1', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(162, '2025-12-14 19:36:47', 'CENTRAL', 'suministro_concedido', 'Suministro concedido para Driver AAA1 en CP 1', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(163, '2025-12-14 19:37:08', 'CP-1', 'inicio_suministro', 'Driver AAA1 iniciando suministro en CP 1', 0);
INSERT INTO `auditoria` (`id_auditoria`, `fecha_hora`, `ip_origen`, `accion`, `descripcion`, `alerta_activa`) VALUES
	(164, '2025-12-14 19:37:14', 'CP-1', 'fin_suministro', 'Fin del suministro del Driver AAA1 en el CP 1', 0);

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
  `dni_conductor` varchar(10) NOT NULL,
  `estado` varchar(50) DEFAULT 'Desconectado'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Volcando datos para la tabla evcharging.conductor: ~16 rows (aproximadamente)
DELETE FROM `conductor`;
INSERT INTO `conductor` (`id_conductor`, `nombre`, `apellidos`, `email_conductor`, `telefono_conductor`, `dni_conductor`, `estado`) VALUES
	('AAA1', 'Cambio2', 'uno', 'pruebaupdate1@gmail.com', '123456789', '12345678U', 'Activo');
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
  `cp_logico` int(11) DEFAULT NULL,
  PRIMARY KEY (`id_punto_recarga`),
  UNIQUE KEY `cp_logico` (`cp_logico`),
  KEY `fk_punto_recarga_central` (`id_central`),
  CONSTRAINT `fk_punto_recarga_central` FOREIGN KEY (`id_central`) REFERENCES `central` (`id_central`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Volcando datos para la tabla evcharging.punto_recarga: ~9 rows (aproximadamente)
DELETE FROM `punto_recarga`;
INSERT INTO `punto_recarga` (`id_punto_recarga`, `id_central`, `ubicacion_punto_recarga`, `precio`, `estado`, `temperatura`, `ultima_actualizacion`, `activo`, `credencial`, `tiene_clave_simetrica`, `cp_logico`) VALUES
	(1, '0039051', 'Prueba4', 3.150, 'ACTIVADO', 17.5, '2025-12-14 18:37:14', 1, NULL, 0, 1);
INSERT INTO `punto_recarga` (`id_punto_recarga`, `id_central`, `ubicacion_punto_recarga`, `precio`, `estado`, `temperatura`, `ultima_actualizacion`, `activo`, `credencial`, `tiene_clave_simetrica`, `cp_logico`) VALUES
	(2, '0039051', 'Zona 2 – EPS 4 – Universidad de Alicante', 0.350, 'DESCONECTADO', 15.6, '2025-12-14 18:09:23', 1, '21def710ca112b069c79515772b24cdc070cd0ddc553e1f3', 0, 2);
INSERT INTO `punto_recarga` (`id_punto_recarga`, `id_central`, `ubicacion_punto_recarga`, `precio`, `estado`, `temperatura`, `ultima_actualizacion`, `activo`, `credencial`, `tiene_clave_simetrica`, `cp_logico`) VALUES
	(3, '0039051', 'Zona 3 – EPS 4 – Universidad de Alicante', 0.350, 'DESCONECTADO', 10.4, '2025-12-14 18:34:06', 1, '58f94002581bee22a141a81376caa2c2568162eb6b35a166', 0, 3);
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
