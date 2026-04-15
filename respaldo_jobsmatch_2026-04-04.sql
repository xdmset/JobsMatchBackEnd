-- MySQL dump 10.13  Distrib 8.0.45, for Linux (x86_64)
--
-- Host: localhost    Database: jobmatch_db
-- ------------------------------------------------------
-- Server version	8.0.45-0ubuntu0.24.04.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `alembic_version`
--

DROP TABLE IF EXISTS `alembic_version`;

CREATE TABLE `alembic_version` (
  `version_num` varchar(32) NOT NULL,
  PRIMARY KEY (`version_num`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

LOCK TABLES `alembic_version` WRITE;
INSERT INTO `alembic_version` VALUES ('h2i3j4k5l6m7');
UNLOCK TABLES;


DROP TABLE IF EXISTS `roles`;

CREATE TABLE `roles` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(50) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `nombre` (`nombre`),
  KEY `ix_roles_id` (`id`),
  CONSTRAINT `nombre_rol` CHECK (`nombre` in ('admin','estudiante','empresa'))
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

LOCK TABLES `roles` WRITE;
INSERT INTO `roles` VALUES
(1,'admin'),
(3,'empresa'),
(2,'estudiante');
UNLOCK TABLES;


DROP TABLE IF EXISTS `usuarios`;

CREATE TABLE `usuarios` (
  `id` int NOT NULL AUTO_INCREMENT,
  `rol_id` int NOT NULL,
  `email` varchar(255) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `is_active` tinyint(1) NOT NULL DEFAULT 1,
  `is_superuser` tinyint(1) NOT NULL DEFAULT 0,
  `is_verified` tinyint(1) NOT NULL DEFAULT 0,
  `es_premium` tinyint(1) DEFAULT 0,
  `fecha_registro` datetime DEFAULT current_timestamp(),
  `fcm_token` varchar(512) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_usuarios_email` (`email`),
  KEY `rol_id` (`rol_id`),
  KEY `ix_usuarios_id` (`id`),
  CONSTRAINT `usuarios_ibfk_1` FOREIGN KEY (`rol_id`) REFERENCES `roles` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=22 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

LOCK TABLES `usuarios` WRITE;
INSERT INTO `usuarios` VALUES
(1,2,'estudiante@test.com','$argon2id$v=19$m=65536,t=3,p=4$hHBu7f3few8h5FzLea8VAg$ZbazLyDANyDJ5S2m6tHnx2oKzsbXrfOgkrH43mxdjXg',1,0,1,0,'2026-02-09 19:05:06',NULL),
(2,3,'empresa@test.com','$argon2id$v=19$m=65536,t=3,p=4$v7f2ntM655wzprSWUorR+g$QKibglY6fWSxq7Iv4hDq40NFMdieQb9S+Z2O1QibuyM',1,0,1,1,'2026-02-09 19:06:34',NULL),
(3,1,'admin@test.com','$argon2id$v=19$m=65536,t=3,p=4$RyhFyPm/lzLGuBcCgBACgA$xJTSdbc3SX0E4i9PBzFm16GUbLHBjMMg+W3geGFB7lo',1,1,1,1,'2026-02-10 13:28:00',NULL),
(4,2,'estudiante2@test.com','$argon2id$v=19$m=65536,t=3,p=4$hHBu7f3few8h5FzLea8VAg$ZbazLyDANyDJ5S2m6tHnx2oKzsbXrfOgkrH43mxdjXg',1,0,1,0,'2026-02-10 14:00:00',NULL),
(5,2,'estudiante3@test.com','$argon2id$v=19$m=65536,t=3,p=4$hHBu7f3few8h5FzLea8VAg$ZbazLyDANyDJ5S2m6tHnx2oKzsbXrfOgkrH43mxdjXg',1,0,1,0,'2026-02-10 14:01:00',NULL),
(6,2,'estudiante4@test.com','$argon2id$v=19$m=65536,t=3,p=4$hHBu7f3few8h5FzLea8VAg$ZbazLyDANyDJ5S2m6tHnx2oKzsbXrfOgkrH43mxdjXg',1,0,1,0,'2026-02-10 14:02:00',NULL),
(7,2,'estudiante5@test.com','$argon2id$v=19$m=65536,t=3,p=4$hHBu7f3few8h5FzLea8VAg$ZbazLyDANyDJ5S2m6tHnx2oKzsbXrfOgkrH43mxdjXg',1,0,1,0,'2026-02-10 14:03:00',NULL),
(8,2,'estudiante6@test.com','$argon2id$v=19$m=65536,t=3,p=4$hHBu7f3few8h5FzLea8VAg$ZbazLyDANyDJ5S2m6tHnx2oKzsbXrfOgkrH43mxdjXg',1,0,1,0,'2026-02-10 14:04:00',NULL),
(9,2,'estudiante7@test.com','$argon2id$v=19$m=65536,t=3,p=4$hHBu7f3few8h5FzLea8VAg$ZbazLyDANyDJ5S2m6tHnx2oKzsbXrfOgkrH43mxdjXg',1,0,1,0,'2026-02-10 14:05:00',NULL),
(10,2,'estudiante8@test.com','$argon2id$v=19$m=65536,t=3,p=4$hHBu7f3few8h5FzLea8VAg$ZbazLyDANyDJ5S2m6tHnx2oKzsbXrfOgkrH43mxdjXg',1,0,1,0,'2026-02-10 14:06:00',NULL),
(11,2,'estudiante9@test.com','$argon2id$v=19$m=65536,t=3,p=4$hHBu7f3few8h5FzLea8VAg$ZbazLyDANyDJ5S2m6tHnx2oKzsbXrfOgkrH43mxdjXg',1,0,1,0,'2026-02-10 14:07:00',NULL),
(12,2,'estudiante10@test.com','$argon2id$v=19$m=65536,t=3,p=4$hHBu7f3few8h5FzLea8VAg$ZbazLyDANyDJ5S2m6tHnx2oKzsbXrfOgkrH43mxdjXg',1,0,1,0,'2026-02-10 14:08:00',NULL),
(13,3,'empresa2@test.com','$argon2id$v=19$m=65536,t=3,p=4$v7f2ntM655wzprSWUorR+g$QKibglY6fWSxq7Iv4hDq40NFMdieQb9S+Z2O1QibuyM',1,0,1,0,'2026-02-10 15:00:00',NULL),
(14,3,'empresa3@test.com','$argon2id$v=19$m=65536,t=3,p=4$v7f2ntM655wzprSWUorR+g$QKibglY6fWSxq7Iv4hDq40NFMdieQb9S+Z2O1QibuyM',1,0,1,0,'2026-02-10 15:01:00',NULL),
(15,3,'empresa4@test.com','$argon2id$v=19$m=65536,t=3,p=4$v7f2ntM655wzprSWUorR+g$QKibglY6fWSxq7Iv4hDq40NFMdieQb9S+Z2O1QibuyM',1,0,1,0,'2026-02-10 15:02:00',NULL),
(16,3,'empresa5@test.com','$argon2id$v=19$m=65536,t=3,p=4$v7f2ntM655wzprSWUorR+g$QKibglY6fWSxq7Iv4hDq40NFMdieQb9S+Z2O1QibuyM',1,0,1,0,'2026-02-10 15:03:00',NULL),
(17,3,'empresa6@test.com','$argon2id$v=19$m=65536,t=3,p=4$v7f2ntM655wzprSWUorR+g$QKibglY6fWSxq7Iv4hDq40NFMdieQb9S+Z2O1QibuyM',1,0,1,0,'2026-02-10 15:04:00',NULL),
(18,3,'empresa7@test.com','$argon2id$v=19$m=65536,t=3,p=4$v7f2ntM655wzprSWUorR+g$QKibglY6fWSxq7Iv4hDq40NFMdieQb9S+Z2O1QibuyM',1,0,1,0,'2026-02-10 15:05:00',NULL),
(19,3,'empresa8@test.com','$argon2id$v=19$m=65536,t=3,p=4$v7f2ntM655wzprSWUorR+g$QKibglY6fWSxq7Iv4hDq40NFMdieQb9S+Z2O1QibuyM',1,0,1,0,'2026-02-10 15:06:00',NULL),
(20,3,'empresa9@test.com','$argon2id$v=19$m=65536,t=3,p=4$v7f2ntM655wzprSWUorR+g$QKibglY6fWSxq7Iv4hDq40NFMdieQb9S+Z2O1QibuyM',1,0,1,0,'2026-02-10 15:07:00',NULL),
(21,3,'empresa10@test.com','$argon2id$v=19$m=65536,t=3,p=4$v7f2ntM655wzprSWUorR+g$QKibglY6fWSxq7Iv4hDq40NFMdieQb9S+Z2O1QibuyM',1,0,1,0,'2026-02-10 15:08:00',NULL);
UNLOCK TABLES;


DROP TABLE IF EXISTS `perfiles_empresas`;

CREATE TABLE `perfiles_empresas` (
  `usuario_id` int NOT NULL,
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
(2,'Tech Solutions','Tecnologia','Empresa de desarrollo de software','https://techsolutions.example','Tijuana, BC',NULL,NULL),
(13,'Norte Digital','Tecnologia','Consultoria de software','https://nortedigital.example','Tijuana, BC',NULL,NULL),
(14,'Baja Logistics','Logistica','Servicios de logistica regional','https://bajalogistics.example','Mexicali, BC',NULL,NULL),
(15,'AgroData','Agroindustria','Analitica para agricultura','https://agrodata.example','Ensenada, BC',NULL,NULL),
(16,'HealthSoft','Salud','Software clinico','https://healthsoft.example','Tijuana, BC',NULL,NULL),
(17,'FinCore','Finanzas','Plataforma de pagos','https://fincore.example','Tijuana, BC',NULL,NULL),
(18,'Oceanic Labs','Investigacion','I+D marino','https://oceaniclabs.example','Ensenada, BC',NULL,NULL),
(19,'RetailNova','Retail','Ecommerce regional','https://retailnova.example','Mexicali, BC',NULL,NULL),
(20,'EduNext','Educacion','Plataforma edtech','https://edunext.example','Tijuana, BC',NULL,NULL),
(21,'GreenGrid','Energia','Soluciones renovables','https://greengrid.example','Rosarito, BC',NULL,NULL);
UNLOCK TABLES;


DROP TABLE IF EXISTS `perfiles_estudiantes`;

CREATE TABLE `perfiles_estudiantes` (
  `usuario_id` int NOT NULL,
  `nombre_completo` varchar(255) DEFAULT NULL,
  `institucion_educativa` varchar(255) DEFAULT NULL,
  `nivel_academico` varchar(255) DEFAULT NULL,
  `biografia` text DEFAULT NULL,
  `habilidades` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL,
  `cv_url` varchar(255) DEFAULT NULL,
  `cv_storage_key` varchar(512) DEFAULT NULL,
  `cv_tipo_archivo` varchar(255) DEFAULT NULL,
  `foto_perfil_url` varchar(255) DEFAULT NULL,
  `foto_perfil_storage_key` varchar(512) DEFAULT NULL,
  `ubicacion` varchar(255) DEFAULT NULL,
  `modalidad_preferida` enum('remoto','presencial','hibrido') DEFAULT NULL,
  `fecha_nacimiento` date DEFAULT NULL,
  PRIMARY KEY (`usuario_id`),
  CONSTRAINT `perfiles_estudiantes_ibfk_1` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

LOCK TABLES `perfiles_estudiantes` WRITE;
INSERT INTO `perfiles_estudiantes` VALUES
(1,'Leonel Test','UTT','TSU','Desarrollador Backend Jr.','{\"python\": \"avanzado\", \"fastapi\": \"intermedio\"}',NULL,NULL,NULL,NULL,NULL,'Tijuana','remoto',NULL),
(4,'Maria Lopez','UABC','Licenciatura','Estudiante de sistemas','{\"java\": \"intermedio\"}',NULL,NULL,NULL,NULL,NULL,'Mexicali','presencial',NULL),
(5,'Carlos Ruiz','ITT','Ingenieria','Apasionado por datos','{\"sql\": \"intermedio\", \"python\": \"basico\"}',NULL,NULL,NULL,NULL,NULL,'Tijuana','hibrido',NULL),
(6,'Ana Perez','UPBC','TSU','Frontend trainee','{\"react\": \"basico\", \"css\": \"intermedio\"}',NULL,NULL,NULL,NULL,NULL,'Ensenada','remoto',NULL),
(7,'Luis Gomez','UABC','Licenciatura','QA junior','{\"testing\": \"intermedio\"}',NULL,NULL,NULL,NULL,NULL,'Tijuana','presencial',NULL),
(8,'Sofia Diaz','CETYS','Ingenieria','Mobile dev','{\"kotlin\": \"basico\"}',NULL,NULL,NULL,NULL,NULL,'Mexicali','hibrido',NULL),
(9,'Diego Torres','UTT','TSU','Backend trainee','{\"node\": \"basico\", \"express\": \"basico\"}',NULL,NULL,NULL,NULL,NULL,'Tijuana','remoto',NULL),
(10,'Valeria Mora','UABC','Licenciatura','UX/UI junior','{\"figma\": \"intermedio\"}',NULL,NULL,NULL,NULL,NULL,'Ensenada','presencial',NULL),
(11,'Jorge Neri','ITT','Ingenieria','DevOps junior','{\"linux\": \"intermedio\", \"docker\": \"basico\"}',NULL,NULL,NULL,NULL,NULL,'Tijuana','hibrido',NULL),
(12,'Fernanda Cruz','UPBC','TSU','Data analyst','{\"excel\": \"avanzado\", \"powerbi\": \"basico\"}',NULL,NULL,NULL,NULL,NULL,'Mexicali','remoto',NULL);
UNLOCK TABLES;


DROP TABLE IF EXISTS `vacantes`;

CREATE TABLE `vacantes` (
  `id` int NOT NULL AUTO_INCREMENT,
  `empresa_id` int NOT NULL,
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
  `id` int NOT NULL AUTO_INCREMENT,
  `estudiante_id` int DEFAULT NULL,
  `vacante_id` int DEFAULT NULL,
  `interes_estudiante` tinyint(1) DEFAULT NULL,
  `fecha` datetime DEFAULT current_timestamp(),
  `fecha_actualizacion` datetime NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_swipe_estudiante_vacante` (`estudiante_id`,`vacante_id`),
  KEY `vacante_id` (`vacante_id`),
  KEY `ix_interacciones_swipe_id` (`id`),
  CONSTRAINT `interacciones_swipe_ibfk_1` FOREIGN KEY (`estudiante_id`) REFERENCES `perfiles_estudiantes` (`usuario_id`),
  CONSTRAINT `interacciones_swipe_ibfk_2` FOREIGN KEY (`vacante_id`) REFERENCES `vacantes` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

LOCK TABLES `interacciones_swipe` WRITE;
INSERT INTO `interacciones_swipe` VALUES
(1,1,1,1,'2026-02-09 19:07:39','2026-04-03 21:02:54');
UNLOCK TABLES;


DROP TABLE IF EXISTS `vacantes_visualizaciones`;

CREATE TABLE `vacantes_visualizaciones` (
  `id` int NOT NULL AUTO_INCREMENT,
  `estudiante_id` int NOT NULL,
  `vacante_id` int NOT NULL,
  `primera_visualizacion` datetime NOT NULL DEFAULT current_timestamp(),
  `ultima_visualizacion` datetime NOT NULL DEFAULT current_timestamp(),
  `total_visualizaciones` int NOT NULL DEFAULT 1,
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
  `id` int NOT NULL AUTO_INCREMENT,
  `empresa_id` int NOT NULL,
  `estudiante_id` int NOT NULL,
  `vacante_id` int NOT NULL,
  `interes_empresa` tinyint(1) NOT NULL,
  `fecha` datetime DEFAULT current_timestamp(),
  `fecha_actualizacion` datetime NOT NULL DEFAULT current_timestamp(),
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
(1,2,1,1,1,'2026-02-09 19:07:48','2026-04-03 21:02:54');
UNLOCK TABLES;


DROP TABLE IF EXISTS `matches`;

CREATE TABLE `matches` (
  `id` int NOT NULL AUTO_INCREMENT,
  `estudiante_id` int DEFAULT NULL,
  `vacante_id` int DEFAULT NULL,
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
  `id` int NOT NULL AUTO_INCREMENT,
  `match_id` int DEFAULT NULL,
  `estudiante_id` int NOT NULL,
  `vacante_id` int NOT NULL,
  `empresa_id` int NOT NULL,
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
  `id` int NOT NULL AUTO_INCREMENT,
  `postulacion_id` int NOT NULL,
  `campos_mejora` text DEFAULT NULL,
  `sugerencias_perfil` text DEFAULT NULL,
  `fecha_envio` datetime DEFAULT current_timestamp(),
  `roadmap_json` json DEFAULT NULL,
  `roadmap_estado` varchar(50) NOT NULL DEFAULT 'pendiente',
  `roadmap_generado_en` datetime DEFAULT NULL,
  `roadmap_error` text DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_retro_postulacion` (`postulacion_id`),
  KEY `ix_retroalimentacion_id` (`id`),
  CONSTRAINT `retroalimentacion_ibfk_1` FOREIGN KEY (`postulacion_id`) REFERENCES `postulaciones` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

LOCK TABLES `retroalimentacion` WRITE;
UNLOCK TABLES;


DROP TABLE IF EXISTS `suscripciones`;

CREATE TABLE `suscripciones` (
  `id` int NOT NULL AUTO_INCREMENT,
  `usuario_id` int NOT NULL,
  `tipo_plan` enum('free','premium') NOT NULL,
  `fecha_inicio` date DEFAULT NULL,
  `fecha_fin` date DEFAULT NULL,
  `origen_pago` enum('manual','paypal') NOT NULL DEFAULT 'manual',
  `paypal_plan_id` varchar(64) DEFAULT NULL,
  `paypal_subscription_id` varchar(64) DEFAULT NULL,
  `estado_externo` varchar(64) DEFAULT NULL,
  `moneda` varchar(3) DEFAULT NULL,
  `monto` decimal(10,2) DEFAULT NULL,
  `detalle_externo` text DEFAULT NULL,
  `rol_objetivo` enum('estudiante','empresa') NOT NULL,
  `codigo_plan` varchar(64) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_suscripciones_id` (`id`),
  UNIQUE KEY `ix_suscripciones_paypal_subscription_id` (`paypal_subscription_id`),
  KEY `usuario_id` (`usuario_id`),
  CONSTRAINT `suscripciones_ibfk_1` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

LOCK TABLES `suscripciones` WRITE;
INSERT INTO `suscripciones` VALUES
(1,1,'free','2026-02-09',NULL,'manual',NULL,NULL,NULL,NULL,NULL,NULL,'estudiante','free_estudiante'),
(2,2,'premium','2026-02-09',NULL,'manual',NULL,NULL,NULL,NULL,NULL,NULL,'empresa','premium_empresa'),
(3,3,'premium','2026-02-10',NULL,'manual',NULL,NULL,NULL,NULL,NULL,NULL,'estudiante','premium_estudiante');
UNLOCK TABLES;


DROP TABLE IF EXISTS `planes`;

CREATE TABLE `planes` (
  `id` int NOT NULL AUTO_INCREMENT,
  `codigo` varchar(64) NOT NULL,
  `nombre` varchar(100) NOT NULL,
  `paypal_product_id` varchar(64) NOT NULL,
  `paypal_plan_id` varchar(64) NOT NULL,
  `moneda` varchar(3) NOT NULL,
  `precio` decimal(10,2) NOT NULL,
  `intervalo_unidad` varchar(16) NOT NULL,
  `intervalo_conteo` int NOT NULL,
  `activo` tinyint(1) NOT NULL DEFAULT 1,
  `rol_objetivo` enum('estudiante','empresa') NOT NULL,
  `periodicidad` enum('mensual','semestral','anual') NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `codigo` (`codigo`),
  UNIQUE KEY `paypal_plan_id` (`paypal_plan_id`),
  KEY `ix_planes_id` (`id`),
  KEY `ix_planes_paypal_plan_id` (`paypal_plan_id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

LOCK TABLES `planes` WRITE;
UNLOCK TABLES;


DROP TABLE IF EXISTS `notificaciones`;

CREATE TABLE `notificaciones` (
  `id` int NOT NULL AUTO_INCREMENT,
  `usuario_id` int NOT NULL,
  `tipo` enum('like_recibido','match','postulacion_estado') NOT NULL,
  `titulo` varchar(255) NOT NULL,
  `mensaje` text NOT NULL,
  `vacante_id` int DEFAULT NULL,
  `postulacion_id` int DEFAULT NULL,
  `estudiante_id` int DEFAULT NULL,
  `leida` tinyint(1) NOT NULL DEFAULT 0,
  `fecha_creacion` datetime NOT NULL DEFAULT now(),
  `fecha_leida` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `vacante_id` (`vacante_id`),
  KEY `postulacion_id` (`postulacion_id`),
  KEY `estudiante_id` (`estudiante_id`),
  KEY `ix_notificaciones_id` (`id`),
  KEY `ix_notificaciones_usuario_id` (`usuario_id`),
  KEY `ix_notificaciones_leida` (`leida`),
  KEY `ix_notificaciones_fecha_creacion` (`fecha_creacion`),
  CONSTRAINT `notificaciones_ibfk_1` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`) ON DELETE CASCADE,
  CONSTRAINT `notificaciones_ibfk_2` FOREIGN KEY (`vacante_id`) REFERENCES `vacantes` (`id`) ON DELETE SET NULL,
  CONSTRAINT `notificaciones_ibfk_3` FOREIGN KEY (`postulacion_id`) REFERENCES `postulaciones` (`id`) ON DELETE SET NULL,
  CONSTRAINT `notificaciones_ibfk_4` FOREIGN KEY (`estudiante_id`) REFERENCES `perfiles_estudiantes` (`usuario_id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

LOCK TABLES `notificaciones` WRITE;
UNLOCK TABLES;

--
-- Dumping routines for database 'jobmatch_db'
--
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-04-15  9:39:34
