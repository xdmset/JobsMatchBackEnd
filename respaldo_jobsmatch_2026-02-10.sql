/*M!999999\- enable the sandbox mode */
-- MariaDB dump 10.19  Distrib 10.11.15-MariaDB, for Linux (x86_64)
--
-- Host: localhost    Database: jobsmatch
-- ------------------------------------------------------
-- Server version    10.11.15-MariaDB

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

DROP TABLE IF EXISTS `alembic_version`;
CREATE TABLE `alembic_version` (
  `version_num` varchar(32) NOT NULL,
  PRIMARY KEY (`version_num`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

LOCK TABLES `alembic_version` WRITE;
INSERT INTO `alembic_version` VALUES ('d2f6e7a1c9ab');
UNLOCK TABLES;

DROP TABLE IF EXISTS `roles`;
CREATE TABLE `roles` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(50) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `nombre` (`nombre`),
  KEY `ix_roles_id` (`id`),
  CONSTRAINT `nombre_rol` CHECK (`nombre` in ('admin','estudiante','empresa'))
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

LOCK TABLES `roles` WRITE;
INSERT INTO `roles` VALUES
(1,'admin'),
(2,'estudiante'),
(3,'empresa');
UNLOCK TABLES;

DROP TABLE IF EXISTS `usuarios`;
CREATE TABLE `usuarios` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `rol_id` int(11) NOT NULL,
  `email` varchar(255) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `is_active` tinyint(1) NOT NULL DEFAULT 1,
  `is_superuser` tinyint(1) NOT NULL DEFAULT 0,
  `is_verified` tinyint(1) NOT NULL DEFAULT 0,
  `es_premium` tinyint(1) DEFAULT 0,
  `fecha_registro` datetime DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_usuarios_email` (`email`),
  KEY `rol_id` (`rol_id`),
  KEY `ix_usuarios_id` (`id`),
  CONSTRAINT `usuarios_ibfk_1` FOREIGN KEY (`rol_id`) REFERENCES `roles` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

LOCK TABLES `usuarios` WRITE;
INSERT INTO `usuarios` VALUES
(1,2,'estudiante@test.com','$argon2id$v=19$m=65536,t=3,p=4$demo_student_hash',1,0,1,0,'2026-02-09 19:05:06'),
(2,3,'empresa@test.com','$argon2id$v=19$m=65536,t=3,p=4$demo_company_hash',1,0,1,1,'2026-02-09 19:06:34'),
(3,1,'admin@test.com','$argon2id$v=19$m=65536,t=3,p=4$RyhFyPm/lzLGuBcCgBACgA$xJTSdbc3SX0E4i9PBzFm16GUbLHBjMMg+W3geGFB7lo',1,1,1,1,'2026-02-10 13:28:00');
UNLOCK TABLES;

DROP TABLE IF EXISTS `perfiles_empresas`;
CREATE TABLE `perfiles_empresas` (
  `usuario_id` int(11) NOT NULL,
  `nombre_comercial` varchar(255) NOT NULL,
  `sector` varchar(255) DEFAULT NULL,
  `descripcion` text DEFAULT NULL,
  `sitio_web` varchar(255) DEFAULT NULL,
  `ubicacion_sede` varchar(255) DEFAULT NULL,
  `foto_perfil_url` varchar(255) DEFAULT NULL,
  `foto_perfil_storage_key` varchar(512) DEFAULT NULL,
  PRIMARY KEY (`usuario_id`),
  CONSTRAINT `perfiles_empresas_ibfk_1` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

LOCK TABLES `perfiles_empresas` WRITE;
INSERT INTO `perfiles_empresas` VALUES
(2,'Tech Solutions','Tecnologia','Empresa de desarrollo de software','https://techsolutions.example','Tijuana, BC',NULL,NULL);
UNLOCK TABLES;

DROP TABLE IF EXISTS `perfiles_estudiantes`;
CREATE TABLE `perfiles_estudiantes` (
  `usuario_id` int(11) NOT NULL,
  `nombre_completo` varchar(255) DEFAULT NULL,
  `institucion_educativa` varchar(255) DEFAULT NULL,
  `nivel_academico` varchar(255) DEFAULT NULL,
  `biografia` text DEFAULT NULL,
  `habilidades` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`habilidades`)),
  `cv_url` varchar(255) DEFAULT NULL,
  `cv_storage_key` varchar(512) DEFAULT NULL,
  `cv_tipo_archivo` varchar(255) DEFAULT NULL,
  `foto_perfil_url` varchar(255) DEFAULT NULL,
  `foto_perfil_storage_key` varchar(512) DEFAULT NULL,
  `fecha_nacimiento` date DEFAULT NULL,
  `ubicacion` varchar(255) DEFAULT NULL,
  `modalidad_preferida` enum('remoto','presencial','hibrido') DEFAULT NULL,
  PRIMARY KEY (`usuario_id`),
  CONSTRAINT `perfiles_estudiantes_ibfk_1` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

LOCK TABLES `perfiles_estudiantes` WRITE;
INSERT INTO `perfiles_estudiantes` VALUES
(1,'Leonel Test','UTT','TSU','Desarrollador Backend Jr.','{\"python\": \"avanzado\", \"fastapi\": \"intermedio\"}',NULL,NULL,NULL,NULL,NULL,'2002-09-18','Tijuana','remoto');
UNLOCK TABLES;

DROP TABLE IF EXISTS `vacantes`;
CREATE TABLE `vacantes` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `empresa_id` int(11) NOT NULL,
  `titulo` varchar(255) NOT NULL,
  `descripcion` text DEFAULT NULL,
  `requisitos` text DEFAULT NULL,
  `tipo_contrato` varchar(255) DEFAULT NULL,
  `modalidad` enum('remoto','presencial','hibrido') DEFAULT NULL,
  `ubicacion` varchar(255) DEFAULT NULL,
  `sueldo_minimo` decimal(10,2) DEFAULT NULL,
  `sueldo_maximo` decimal(10,2) DEFAULT NULL,
  `moneda` varchar(255) DEFAULT 'MXN',
  `estado` enum('activa','pausada','cerrada') DEFAULT 'activa',
  `fecha_publicacion` datetime DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  KEY `empresa_id` (`empresa_id`),
  KEY `ix_vacantes_id` (`id`),
  KEY `idx_vacantes_empresa_estado` (`empresa_id`,`estado`),
  CONSTRAINT `vacantes_ibfk_1` FOREIGN KEY (`empresa_id`) REFERENCES `perfiles_empresas` (`usuario_id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

LOCK TABLES `vacantes` WRITE;
INSERT INTO `vacantes` VALUES
(1,2,'Backend Developer Python','Desarrollo de APIs con FastAPI','Conocimientos en SQL y Python',NULL,'remoto','Tijuana, BC',15000.00,20000.00,'MXN','activa','2026-02-09 19:07:31'),
(2,2,'Frontend Developer React','Desarrollo de interfaces web','React y CSS avanzado',NULL,'hibrido','Tijuana, BC',12000.00,18000.00,'MXN','activa','2026-02-09 19:07:31');
UNLOCK TABLES;

DROP TABLE IF EXISTS `interacciones_swipe`;
CREATE TABLE `interacciones_swipe` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `estudiante_id` int(11) DEFAULT NULL,
  `vacante_id` int(11) DEFAULT NULL,
  `interes_estudiante` tinyint(1) DEFAULT NULL,
  `fecha` datetime DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_swipe_estudiante_vacante` (`estudiante_id`,`vacante_id`),
  KEY `vacante_id` (`vacante_id`),
  KEY `ix_interacciones_swipe_id` (`id`),
  CONSTRAINT `interacciones_swipe_ibfk_1` FOREIGN KEY (`estudiante_id`) REFERENCES `perfiles_estudiantes` (`usuario_id`),
  CONSTRAINT `interacciones_swipe_ibfk_2` FOREIGN KEY (`vacante_id`) REFERENCES `vacantes` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

LOCK TABLES `interacciones_swipe` WRITE;
INSERT INTO `interacciones_swipe` VALUES
(1,1,1,1,'2026-02-09 19:07:39');
UNLOCK TABLES;

DROP TABLE IF EXISTS `vacantes_visualizaciones`;
CREATE TABLE `vacantes_visualizaciones` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `estudiante_id` int(11) NOT NULL,
  `vacante_id` int(11) NOT NULL,
  `primera_visualizacion` datetime NOT NULL DEFAULT current_timestamp(),
  `ultima_visualizacion` datetime NOT NULL DEFAULT current_timestamp(),
  `total_visualizaciones` int(11) NOT NULL DEFAULT 1,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_visualizacion_estudiante_vacante` (`estudiante_id`,`vacante_id`),
  KEY `ix_vacantes_visualizaciones_id` (`id`),
  KEY `vacante_visualizacion_vacante_id` (`vacante_id`),
  CONSTRAINT `vacantes_visualizaciones_ibfk_1` FOREIGN KEY (`estudiante_id`) REFERENCES `perfiles_estudiantes` (`usuario_id`),
  CONSTRAINT `vacantes_visualizaciones_ibfk_2` FOREIGN KEY (`vacante_id`) REFERENCES `vacantes` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

LOCK TABLES `vacantes_visualizaciones` WRITE;
INSERT INTO `vacantes_visualizaciones` VALUES
(1,1,1,'2026-02-09 19:07:35','2026-02-09 19:07:39',2);
UNLOCK TABLES;

DROP TABLE IF EXISTS `interacciones_swipe_empresa`;
CREATE TABLE `interacciones_swipe_empresa` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `empresa_id` int(11) NOT NULL,
  `estudiante_id` int(11) NOT NULL,
  `vacante_id` int(11) NOT NULL,
  `interes_empresa` tinyint(1) NOT NULL,
  `fecha` datetime DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_swipe_empresa_tripleta` (`empresa_id`,`estudiante_id`,`vacante_id`),
  KEY `ix_interacciones_swipe_empresa_id` (`id`),
  KEY `estudiante_id` (`estudiante_id`),
  KEY `vacante_id` (`vacante_id`),
  CONSTRAINT `interacciones_swipe_empresa_ibfk_1` FOREIGN KEY (`empresa_id`) REFERENCES `perfiles_empresas` (`usuario_id`),
  CONSTRAINT `interacciones_swipe_empresa_ibfk_2` FOREIGN KEY (`estudiante_id`) REFERENCES `perfiles_estudiantes` (`usuario_id`),
  CONSTRAINT `interacciones_swipe_empresa_ibfk_3` FOREIGN KEY (`vacante_id`) REFERENCES `vacantes` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

LOCK TABLES `interacciones_swipe_empresa` WRITE;
INSERT INTO `interacciones_swipe_empresa` VALUES
(1,2,1,1,1,'2026-02-09 19:07:48');
UNLOCK TABLES;

DROP TABLE IF EXISTS `matches`;
CREATE TABLE `matches` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `estudiante_id` int(11) DEFAULT NULL,
  `vacante_id` int(11) DEFAULT NULL,
  `fecha_match` datetime DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_match_estudiante_vacante` (`estudiante_id`,`vacante_id`),
  KEY `vacante_id` (`vacante_id`),
  KEY `ix_matches_id` (`id`),
  CONSTRAINT `matches_ibfk_1` FOREIGN KEY (`estudiante_id`) REFERENCES `perfiles_estudiantes` (`usuario_id`),
  CONSTRAINT `matches_ibfk_2` FOREIGN KEY (`vacante_id`) REFERENCES `vacantes` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

LOCK TABLES `matches` WRITE;
INSERT INTO `matches` VALUES
(1,1,1,'2026-02-09 19:07:48');
UNLOCK TABLES;

DROP TABLE IF EXISTS `postulaciones`;
CREATE TABLE `postulaciones` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `match_id` int(11) DEFAULT NULL,
  `estudiante_id` int(11) NOT NULL,
  `vacante_id` int(11) NOT NULL,
  `empresa_id` int(11) NOT NULL,
  `source` enum('app_swipe','web_apply') NOT NULL,
  `estado` enum('enviado','visto','en_proceso','rechazado','aceptado') NOT NULL DEFAULT 'enviado',
  `fecha_creacion` datetime NOT NULL DEFAULT current_timestamp(),
  `fecha_actualizacion` datetime NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  KEY `match_id` (`match_id`),
  KEY `ix_postulaciones_id` (`id`),
  KEY `idx_postulaciones_est_vac_estado` (`estudiante_id`,`vacante_id`,`estado`,`fecha_actualizacion`),
  KEY `idx_postulaciones_empresa_estado` (`empresa_id`,`estado`,`fecha_actualizacion`),
  CONSTRAINT `fk_post_empresa` FOREIGN KEY (`empresa_id`) REFERENCES `perfiles_empresas` (`usuario_id`),
  CONSTRAINT `fk_post_estudiante` FOREIGN KEY (`estudiante_id`) REFERENCES `perfiles_estudiantes` (`usuario_id`),
  CONSTRAINT `fk_post_vacante` FOREIGN KEY (`vacante_id`) REFERENCES `vacantes` (`id`),
  CONSTRAINT `postulaciones_ibfk_1` FOREIGN KEY (`match_id`) REFERENCES `matches` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

LOCK TABLES `postulaciones` WRITE;
INSERT INTO `postulaciones` VALUES
(1,1,1,1,2,'app_swipe','enviado','2026-02-09 19:07:48','2026-02-09 19:07:48');
UNLOCK TABLES;

DROP TABLE IF EXISTS `retroalimentacion`;
CREATE TABLE `retroalimentacion` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `postulacion_id` int(11) NOT NULL,
  `campos_mejora` text DEFAULT NULL,
  `sugerencias_perfil` text DEFAULT NULL,
  `fecha_envio` datetime DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_retro_postulacion` (`postulacion_id`),
  KEY `ix_retroalimentacion_id` (`id`),
  CONSTRAINT `retroalimentacion_ibfk_1` FOREIGN KEY (`postulacion_id`) REFERENCES `postulaciones` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

LOCK TABLES `retroalimentacion` WRITE;
UNLOCK TABLES;

DROP TABLE IF EXISTS `suscripciones`;
CREATE TABLE `suscripciones` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `usuario_id` int(11) NOT NULL,
  `tipo_plan` enum('free','premium') NOT NULL,
  `fecha_inicio` date DEFAULT NULL,
  `fecha_fin` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_suscripciones_id` (`id`),
  KEY `usuario_id` (`usuario_id`),
  CONSTRAINT `suscripciones_ibfk_1` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

LOCK TABLES `suscripciones` WRITE;
INSERT INTO `suscripciones` VALUES
(1,1,'free','2026-02-09',NULL),
(2,2,'premium','2026-02-09',NULL),
(3,3,'premium','2026-02-10',NULL);
UNLOCK TABLES;

/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;
/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-03-09 02:00:00
