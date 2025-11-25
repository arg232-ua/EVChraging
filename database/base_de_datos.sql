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
	('AAA1', 'Alejandro', 'Sánchez Martínez', 'alejandrosd2526@gmail.com', '601257198', '45983261Z');
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
	('AAA16', 'Nuevo', 'Conductor uno', 'pruebanuevo1@gmail.com', '683495035', '12439045H');

-- Volcando estructura para tabla evcharging.punto_recarga
CREATE TABLE IF NOT EXISTS `punto_recarga` (
  `id_punto_recarga` int(11) NOT NULL AUTO_INCREMENT,
  `id_central` varchar(10) NOT NULL,
  `ubicacion_punto_recarga` varchar(255) NOT NULL,
  `precio` decimal(8,3) NOT NULL,
  `estado` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`id_punto_recarga`),
  KEY `fk_punto_recarga_central` (`id_central`),
  CONSTRAINT `fk_punto_recarga_central` FOREIGN KEY (`id_central`) REFERENCES `central` (`id_central`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Volcando datos para la tabla evcharging.punto_recarga: ~3 rows (aproximadamente)
DELETE FROM `punto_recarga`;
INSERT INTO `punto_recarga` (`id_punto_recarga`, `id_central`, `ubicacion_punto_recarga`, `precio`, `estado`) VALUES
	(1, '0039051', 'Zona 1 – EPS 4 – Universidad de Alicante', 0.350, 'DESCONECTADO');
INSERT INTO `punto_recarga` (`id_punto_recarga`, `id_central`, `ubicacion_punto_recarga`, `precio`, `estado`) VALUES
	(2, '0039051', 'Zona 2 – EPS 4 – Universidad de Alicante', 0.350, 'DESCONECTADO');
INSERT INTO `punto_recarga` (`id_punto_recarga`, `id_central`, `ubicacion_punto_recarga`, `precio`, `estado`) VALUES
	(3, '0039051', 'Zona 3 – EPS 4 – Universidad de Alicante', 0.350, 'DESCONECTADO');

/*!40103 SET TIME_ZONE=IFNULL(@OLD_TIME_ZONE, 'system') */;
/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IFNULL(@OLD_FOREIGN_KEY_CHECKS, 1) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40111 SET SQL_NOTES=IFNULL(@OLD_SQL_NOTES, 1) */;
