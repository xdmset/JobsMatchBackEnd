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
INSERT INTO `alembic_version` VALUES ('a1d4f8b2c3e7');
UNLOCK TABLES;

DROP TABLE IF EXISTS `roles`;
CREATE TABLE `roles` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(50) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `nombre` (`nombre`),
  KEY `ix_roles_id` (`id`),
  CONSTRAINT `nombre_rol` CHECK (`nombre` in ('admin','estudiante','empresa'))
) ENGINE=InnoDB AUTO_INCREMENT=22 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

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
) ENGINE=InnoDB AUTO_INCREMENT=22 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

LOCK TABLES `usuarios` WRITE;
INSERT INTO `usuarios` VALUES
(1,2,'estudiante1@test.com','$argon2id$v=19$m=65536,t=3,p=4$hHBu7f3few8h5FzLea8VAg$ZbazLyDANyDJ5S2m6tHnx2oKzsbXrfOgkrH43mxdjXg',1,0,1,0,'2026-02-09 19:05:06'),
(2,3,'empresa1@test.com','$argon2id$v=19$m=65536,t=3,p=4$v7f2ntM655wzprSWUorR+g$QKibglY6fWSxq7Iv4hDq40NFMdieQb9S+Z2O1QibuyM',1,0,1,1,'2026-02-09 19:06:34'),
(3,1,'admin@test.com','$argon2id$v=19$m=65536,t=3,p=4$RyhFyPm/lzLGuBcCgBACgA$xJTSdbc3SX0E4i9PBzFm16GUbLHBjMMg+W3geGFB7lo',1,1,1,1,'2026-02-10 13:28:00'),
(4,2,'estudiante2@test.com','$argon2id$v=19$m=65536,t=3,p=4$hHBu7f3few8h5FzLea8VAg$ZbazLyDANyDJ5S2m6tHnx2oKzsbXrfOgkrH43mxdjXg',1,0,1,0,'2026-02-10 14:00:00'),
(5,2,'estudiante3@test.com','$argon2id$v=19$m=65536,t=3,p=4$hHBu7f3few8h5FzLea8VAg$ZbazLyDANyDJ5S2m6tHnx2oKzsbXrfOgkrH43mxdjXg',1,0,1,0,'2026-02-10 14:01:00'),
(6,2,'estudiante4@test.com','$argon2id$v=19$m=65536,t=3,p=4$hHBu7f3few8h5FzLea8VAg$ZbazLyDANyDJ5S2m6tHnx2oKzsbXrfOgkrH43mxdjXg',1,0,1,0,'2026-02-10 14:02:00'),
(7,2,'estudiante5@test.com','$argon2id$v=19$m=65536,t=3,p=4$hHBu7f3few8h5FzLea8VAg$ZbazLyDANyDJ5S2m6tHnx2oKzsbXrfOgkrH43mxdjXg',1,0,1,0,'2026-02-10 14:03:00'),
(8,2,'estudiante6@test.com','$argon2id$v=19$m=65536,t=3,p=4$hHBu7f3few8h5FzLea8VAg$ZbazLyDANyDJ5S2m6tHnx2oKzsbXrfOgkrH43mxdjXg',1,0,1,0,'2026-02-10 14:04:00'),
(9,2,'estudiante7@test.com','$argon2id$v=19$m=65536,t=3,p=4$hHBu7f3few8h5FzLea8VAg$ZbazLyDANyDJ5S2m6tHnx2oKzsbXrfOgkrH43mxdjXg',1,0,1,0,'2026-02-10 14:05:00'),
(10,2,'estudiante8@test.com','$argon2id$v=19$m=65536,t=3,p=4$hHBu7f3few8h5FzLea8VAg$ZbazLyDANyDJ5S2m6tHnx2oKzsbXrfOgkrH43mxdjXg',1,0,1,0,'2026-02-10 14:06:00'),
(11,2,'estudiante9@test.com','$argon2id$v=19$m=65536,t=3,p=4$hHBu7f3few8h5FzLea8VAg$ZbazLyDANyDJ5S2m6tHnx2oKzsbXrfOgkrH43mxdjXg',1,0,1,0,'2026-02-10 14:07:00'),
(12,2,'estudiante10@test.com','$argon2id$v=19$m=65536,t=3,p=4$hHBu7f3few8h5FzLea8VAg$ZbazLyDANyDJ5S2m6tHnx2oKzsbXrfOgkrH43mxdjXg',1,0,1,0,'2026-02-10 14:08:00'),
(13,3,'empresa2@test.com','$argon2id$v=19$m=65536,t=3,p=4$v7f2ntM655wzprSWUorR+g$QKibglY6fWSxq7Iv4hDq40NFMdieQb9S+Z2O1QibuyM',1,0,1,0,'2026-02-10 15:00:00'),
(14,3,'empresa3@test.com','$argon2id$v=19$m=65536,t=3,p=4$v7f2ntM655wzprSWUorR+g$QKibglY6fWSxq7Iv4hDq40NFMdieQb9S+Z2O1QibuyM',1,0,1,0,'2026-02-10 15:01:00'),
(15,3,'empresa4@test.com','$argon2id$v=19$m=65536,t=3,p=4$v7f2ntM655wzprSWUorR+g$QKibglY6fWSxq7Iv4hDq40NFMdieQb9S+Z2O1QibuyM',1,0,1,0,'2026-02-10 15:02:00'),
(16,3,'empresa5@test.com','$argon2id$v=19$m=65536,t=3,p=4$v7f2ntM655wzprSWUorR+g$QKibglY6fWSxq7Iv4hDq40NFMdieQb9S+Z2O1QibuyM',1,0,1,0,'2026-02-10 15:03:00'),
(17,3,'empresa6@test.com','$argon2id$v=19$m=65536,t=3,p=4$v7f2ntM655wzprSWUorR+g$QKibglY6fWSxq7Iv4hDq40NFMdieQb9S+Z2O1QibuyM',1,0,1,0,'2026-02-10 15:04:00'),
(18,3,'empresa7@test.com','$argon2id$v=19$m=65536,t=3,p=4$v7f2ntM655wzprSWUorR+g$QKibglY6fWSxq7Iv4hDq40NFMdieQb9S+Z2O1QibuyM',1,0,1,0,'2026-02-10 15:05:00'),
(19,3,'empresa8@test.com','$argon2id$v=19$m=65536,t=3,p=4$v7f2ntM655wzprSWUorR+g$QKibglY6fWSxq7Iv4hDq40NFMdieQb9S+Z2O1QibuyM',1,0,1,0,'2026-02-10 15:06:00'),
(20,3,'empresa9@test.com','$argon2id$v=19$m=65536,t=3,p=4$v7f2ntM655wzprSWUorR+g$QKibglY6fWSxq7Iv4hDq40NFMdieQb9S+Z2O1QibuyM',1,0,1,0,'2026-02-10 15:07:00'),
(21,3,'empresa10@test.com','$argon2id$v=19$m=65536,t=3,p=4$v7f2ntM655wzprSWUorR+g$QKibglY6fWSxq7Iv4hDq40NFMdieQb9S+Z2O1QibuyM',1,0,1,0,'2026-02-10 15:08:00');
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
(1,'Leonel Test','UTT','TSU','Desarrollador Backend Jr.','{\"python\": \"avanzado\", \"fastapi\": \"intermedio\"}',NULL,NULL,NULL,NULL,NULL,'2002-09-18','Tijuana','remoto'),
(4,'Maria Lopez','UABC','Licenciatura','Estudiante de sistemas','{\"java\": \"intermedio\"}',NULL,NULL,NULL,NULL,NULL,'2001-03-12','Mexicali','presencial'),
(5,'Carlos Ruiz','ITT','Ingenieria','Apasionado por datos','{\"sql\": \"intermedio\", \"python\": \"basico\"}',NULL,NULL,NULL,NULL,NULL,'2000-07-25','Tijuana','hibrido'),
(6,'Ana Perez','UPBC','TSU','Frontend trainee','{\"react\": \"basico\", \"css\": \"intermedio\"}',NULL,NULL,NULL,NULL,NULL,'2003-01-09','Ensenada','remoto'),
(7,'Luis Gomez','UABC','Licenciatura','QA junior','{\"testing\": \"intermedio\"}',NULL,NULL,NULL,NULL,NULL,'2001-11-30','Tijuana','presencial'),
(8,'Sofia Diaz','CETYS','Ingenieria','Mobile dev','{\"kotlin\": \"basico\"}',NULL,NULL,NULL,NULL,NULL,'2002-05-18','Mexicali','hibrido'),
(9,'Diego Torres','UTT','TSU','Backend trainee','{\"node\": \"basico\", \"express\": \"basico\"}',NULL,NULL,NULL,NULL,NULL,'2003-08-14','Tijuana','remoto'),
(10,'Valeria Mora','UABC','Licenciatura','UX/UI junior','{\"figma\": \"intermedio\"}',NULL,NULL,NULL,NULL,NULL,'2001-09-22','Ensenada','presencial'),
(11,'Jorge Neri','ITT','Ingenieria','DevOps junior','{\"linux\": \"intermedio\", \"docker\": \"basico\"}',NULL,NULL,NULL,NULL,NULL,'2000-12-03','Tijuana','hibrido'),
(12,'Fernanda Cruz','UPBC','TSU','Data analyst','{\"excel\": \"avanzado\", \"powerbi\": \"basico\"}',NULL,NULL,NULL,NULL,NULL,'2002-02-27','Mexicali','remoto');
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
) ENGINE=InnoDB AUTO_INCREMENT=51 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

LOCK TABLES `vacantes` WRITE;
INSERT INTO `vacantes` VALUES
(1,2,'Backend Developer Python','Desarrollo de APIs con FastAPI','Conocimientos en SQL y Python',NULL,'remoto','Tijuana, BC',15000.00,20000.00,'MXN','activa','2026-02-09 19:07:31'),
(2,2,'Frontend Developer React','Desarrollo de interfaces web','React y CSS avanzado',NULL,'hibrido','Tijuana, BC',12000.00,18000.00,'MXN','activa','2026-02-09 19:07:31'),
(3,2,'QA Automation Jr','Pruebas automatizadas de API y UI','Python y Selenium',NULL,'hibrido','Tijuana, BC',12000.00,17000.00,'MXN','activa','2026-02-10 09:00:00'),
(4,2,'Data Analyst Jr','Analisis de datos y reportes','SQL y Excel',NULL,'remoto','Tijuana, BC',11000.00,16000.00,'MXN','activa','2026-02-10 09:05:00'),
(5,2,'DevOps Intern','Apoyo en CI/CD y monitoreo','Linux y Docker basico',NULL,'presencial','Tijuana, BC',9000.00,13000.00,'MXN','activa','2026-02-10 09:10:00'),
(6,13,'Fullstack Developer','Desarrollo web end to end','Node y React',NULL,'remoto','Tijuana, BC',14000.00,20000.00,'MXN','activa','2026-02-10 10:00:00'),
(7,13,'UX Designer Jr','Diseno de interfaces y prototipos','Figma y principios UX',NULL,'hibrido','Tijuana, BC',11000.00,16000.00,'MXN','activa','2026-02-10 10:05:00'),
(8,13,'Backend Node.js','APIs REST y servicios','Node.js y SQL',NULL,'remoto','Tijuana, BC',13000.00,19000.00,'MXN','activa','2026-02-10 10:10:00'),
(9,13,'Soporte Tecnico','Atencion a clientes y tickets','Windows y redes basico',NULL,'presencial','Tijuana, BC',9000.00,13000.00,'MXN','activa','2026-02-10 10:15:00'),
(10,13,'Mobile Developer','Apps moviles multiplataforma','Flutter o React Native',NULL,'hibrido','Tijuana, BC',13000.00,19000.00,'MXN','activa','2026-02-10 10:20:00'),
(11,14,'Analista de Logistica','Planificacion de rutas y KPIs','Excel y pensamiento analitico',NULL,'presencial','Mexicali, BC',10000.00,15000.00,'MXN','activa','2026-02-10 11:00:00'),
(12,14,'Coordinador de Rutas','Seguimiento de entregas','Comunicacion y organizacion',NULL,'presencial','Mexicali, BC',11000.00,16000.00,'MXN','activa','2026-02-10 11:05:00'),
(13,14,'Desarrollador Integraciones','Integraciones con sistemas externos','APIs y SQL',NULL,'hibrido','Mexicali, BC',13000.00,19000.00,'MXN','activa','2026-02-10 11:10:00'),
(14,14,'Analista de Datos Operativos','Dashboards y reportes','SQL y PowerBI',NULL,'remoto','Mexicali, BC',12000.00,17000.00,'MXN','activa','2026-02-10 11:15:00'),
(15,14,'QA Sistemas','Pruebas funcionales de sistemas','Casos de prueba y reportes',NULL,'hibrido','Mexicali, BC',10000.00,15000.00,'MXN','activa','2026-02-10 11:20:00'),
(16,15,'Data Engineer Jr','Pipelines de datos para agricultura','Python y ETL',NULL,'remoto','Ensenada, BC',13000.00,19000.00,'MXN','activa','2026-02-10 12:00:00'),
(17,15,'Ingeniero IoT','Sensores y telemetria de campo','Electronica y redes',NULL,'presencial','Ensenada, BC',14000.00,20000.00,'MXN','activa','2026-02-10 12:05:00'),
(18,15,'Analista GIS','Mapas y capas geoespaciales','QGIS y analisis espacial',NULL,'hibrido','Ensenada, BC',12000.00,17000.00,'MXN','activa','2026-02-10 12:10:00'),
(19,15,'Backend API','Servicios para plataforma de datos','Python y SQL',NULL,'remoto','Ensenada, BC',13000.00,19000.00,'MXN','activa','2026-02-10 12:15:00'),
(20,15,'Soporte Tecnico Campo','Soporte en sitio a clientes','Atencion y manejo de equipo',NULL,'presencial','Ensenada, BC',9000.00,13000.00,'MXN','activa','2026-02-10 12:20:00'),
(21,16,'QA Clinico','Pruebas de software clinico','Documentacion y pruebas',NULL,'hibrido','Tijuana, BC',12000.00,17000.00,'MXN','activa','2026-02-10 13:00:00'),
(22,16,'Frontend Vue','Interfaces web para salud','Vue y CSS',NULL,'remoto','Tijuana, BC',13000.00,18000.00,'MXN','activa','2026-02-10 13:05:00'),
(23,16,'Backend Java','Servicios y microservicios','Java y SQL',NULL,'hibrido','Tijuana, BC',14000.00,20000.00,'MXN','activa','2026-02-10 13:10:00'),
(24,16,'Soporte Implementacion','Implementacion en clinicas','Capacitacion y soporte',NULL,'presencial','Tijuana, BC',11000.00,16000.00,'MXN','activa','2026-02-10 13:15:00'),
(25,16,'Data Analyst Salud','Analisis de datos clinicos','SQL y Excel',NULL,'remoto','Tijuana, BC',12000.00,17000.00,'MXN','activa','2026-02-10 13:20:00'),
(26,17,'Backend Go','Servicios para pagos','Go y bases de datos',NULL,'remoto','Tijuana, BC',15000.00,22000.00,'MXN','activa','2026-02-10 14:00:00'),
(27,17,'Mobile Flutter','App financiera movil','Flutter y consumo de APIs',NULL,'hibrido','Tijuana, BC',14000.00,20000.00,'MXN','activa','2026-02-10 14:05:00'),
(28,17,'Analista Riesgo','Modelos de riesgo y reportes','Excel y analisis cuantitativo',NULL,'presencial','Tijuana, BC',12000.00,18000.00,'MXN','activa','2026-02-10 14:10:00'),
(29,17,'DevOps Cloud','Infraestructura y despliegues','AWS y CI/CD',NULL,'remoto','Tijuana, BC',15000.00,22000.00,'MXN','activa','2026-02-10 14:15:00'),
(30,17,'Seguridad Aplicaciones','Revision y hardening','OWASP y pruebas basicas',NULL,'hibrido','Tijuana, BC',14000.00,21000.00,'MXN','activa','2026-02-10 14:20:00'),
(31,18,'Investigador Datos','Analisis de datos oceanicos','Python y estadistica',NULL,'presencial','Ensenada, BC',13000.00,19000.00,'MXN','activa','2026-02-10 15:00:00'),
(32,18,'Desarrollador Python','Herramientas de investigacion','Python y APIs',NULL,'remoto','Ensenada, BC',13000.00,19000.00,'MXN','activa','2026-02-10 15:05:00'),
(33,18,'Analista QA','Pruebas de software cientifico','Casos de prueba',NULL,'hibrido','Ensenada, BC',11000.00,16000.00,'MXN','activa','2026-02-10 15:10:00'),
(34,18,'Tecnico Laboratorio','Operacion de equipo de laboratorio','Buenas practicas',NULL,'presencial','Ensenada, BC',10000.00,15000.00,'MXN','activa','2026-02-10 15:15:00'),
(35,18,'Data Visualization','Visualizacion de datos','Python y herramientas BI',NULL,'remoto','Ensenada, BC',12000.00,17000.00,'MXN','activa','2026-02-10 15:20:00'),
(36,19,'Fullstack Ecommerce','Plataforma de ecommerce','React y Node',NULL,'hibrido','Mexicali, BC',14000.00,20000.00,'MXN','activa','2026-02-10 16:00:00'),
(37,19,'Analista Marketing Digital','Campanas y metrics','Ads y analisis web',NULL,'remoto','Mexicali, BC',11000.00,16000.00,'MXN','activa','2026-02-10 16:05:00'),
(38,19,'Especialista SEO','Optimizacion buscadores','SEO onpage y herramientas',NULL,'remoto','Mexicali, BC',11000.00,16000.00,'MXN','activa','2026-02-10 16:10:00'),
(39,19,'Soporte Plataforma','Soporte a vendedores','Atencion y soporte tecnico',NULL,'presencial','Mexicali, BC',9000.00,13000.00,'MXN','activa','2026-02-10 16:15:00'),
(40,19,'Data Engineer','Pipelines y modelado','SQL y ETL',NULL,'hibrido','Mexicali, BC',14000.00,20000.00,'MXN','activa','2026-02-10 16:20:00'),
(41,20,'Frontend React','Plataforma educativa web','React y CSS',NULL,'remoto','Tijuana, BC',13000.00,18000.00,'MXN','activa','2026-02-10 17:00:00'),
(42,20,'Backend Django','Servicios para edtech','Python y Django',NULL,'hibrido','Tijuana, BC',14000.00,20000.00,'MXN','activa','2026-02-10 17:05:00'),
(43,20,'Content Designer','Diseno de contenido educativo','Redaccion y herramientas web',NULL,'remoto','Tijuana, BC',10000.00,15000.00,'MXN','activa','2026-02-10 17:10:00'),
(44,20,'QA Manual','Pruebas manuales de plataforma','Casos de prueba',NULL,'presencial','Tijuana, BC',10000.00,15000.00,'MXN','activa','2026-02-10 17:15:00'),
(45,20,'Data Analyst Educacion','Analisis de uso y KPIs','SQL y BI',NULL,'remoto','Tijuana, BC',12000.00,17000.00,'MXN','activa','2026-02-10 17:20:00'),
(46,21,'Ingeniero Energias Renovables','Proyectos de energia limpia','Ingenieria y gestion',NULL,'presencial','Rosarito, BC',15000.00,22000.00,'MXN','activa','2026-02-10 18:00:00'),
(47,21,'Analista IoT','Sensores y telemetria','Electronica y datos',NULL,'hibrido','Rosarito, BC',13000.00,19000.00,'MXN','activa','2026-02-10 18:05:00'),
(48,21,'Backend API','Servicios para energia','Python y SQL',NULL,'remoto','Rosarito, BC',14000.00,20000.00,'MXN','activa','2026-02-10 18:10:00'),
(49,21,'Project Manager Jr','Coordinacion de proyectos','Planificacion y comunicacion',NULL,'presencial','Rosarito, BC',12000.00,17000.00,'MXN','activa','2026-02-10 18:15:00'),
(50,21,'Data Analyst Energia','Analisis de consumo','SQL y Excel',NULL,'remoto','Rosarito, BC',12000.00,17000.00,'MXN','activa','2026-02-10 18:20:00');
UNLOCK TABLES;

DROP TABLE IF EXISTS `interacciones_swipe`;
CREATE TABLE `interacciones_swipe` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `estudiante_id` int(11) DEFAULT NULL,
  `vacante_id` int(11) DEFAULT NULL,
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
(1,1,1,1,'2026-02-09 19:07:39','2026-02-09 19:07:39');
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
(1,2,1,1,1,'2026-02-09 19:07:48','2026-02-09 19:07:48');
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
  `origen_pago` enum('manual','paypal') NOT NULL DEFAULT 'manual',
  `fecha_inicio` date DEFAULT NULL,
  `fecha_fin` date DEFAULT NULL,
  `paypal_plan_id` varchar(64) DEFAULT NULL,
  `paypal_subscription_id` varchar(64) DEFAULT NULL,
  `estado_externo` varchar(64) DEFAULT NULL,
  `moneda` varchar(3) DEFAULT NULL,
  `monto` decimal(10,2) DEFAULT NULL,
  `detalle_externo` text DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_suscripciones_id` (`id`),
  UNIQUE KEY `ix_suscripciones_paypal_subscription_id` (`paypal_subscription_id`),
  KEY `usuario_id` (`usuario_id`),
  CONSTRAINT `suscripciones_ibfk_1` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

LOCK TABLES `suscripciones` WRITE;
INSERT INTO `suscripciones` VALUES
(1,1,'free','manual','2026-02-09',NULL,NULL,NULL,NULL,NULL,NULL,NULL),
(2,2,'premium','manual','2026-02-09',NULL,NULL,NULL,NULL,NULL,NULL,NULL),
(3,3,'premium','manual','2026-02-10',NULL,NULL,NULL,NULL,NULL,NULL,NULL),
(4,4,'free','manual','2026-02-10',NULL,NULL,NULL,NULL,NULL,NULL,NULL),
(5,5,'free','manual','2026-02-10',NULL,NULL,NULL,NULL,NULL,NULL,NULL),
(6,6,'free','manual','2026-02-10',NULL,NULL,NULL,NULL,NULL,NULL,NULL),
(7,7,'free','manual','2026-02-10',NULL,NULL,NULL,NULL,NULL,NULL,NULL),
(8,8,'free','manual','2026-02-10',NULL,NULL,NULL,NULL,NULL,NULL,NULL),
(9,9,'free','manual','2026-02-10',NULL,NULL,NULL,NULL,NULL,NULL,NULL),
(10,10,'free','manual','2026-02-10',NULL,NULL,NULL,NULL,NULL,NULL,NULL),
(11,11,'free','manual','2026-02-10',NULL,NULL,NULL,NULL,NULL,NULL,NULL),
(12,12,'free','manual','2026-02-10',NULL,NULL,NULL,NULL,NULL,NULL,NULL),
(13,13,'free','manual','2026-02-10',NULL,NULL,NULL,NULL,NULL,NULL,NULL),
(14,14,'free','manual','2026-02-10',NULL,NULL,NULL,NULL,NULL,NULL,NULL),
(15,15,'free','manual','2026-02-10',NULL,NULL,NULL,NULL,NULL,NULL,NULL),
(16,16,'free','manual','2026-02-10',NULL,NULL,NULL,NULL,NULL,NULL,NULL),
(17,17,'free','manual','2026-02-10',NULL,NULL,NULL,NULL,NULL,NULL,NULL),
(18,18,'free','manual','2026-02-10',NULL,NULL,NULL,NULL,NULL,NULL,NULL),
(19,19,'free','manual','2026-02-10',NULL,NULL,NULL,NULL,NULL,NULL,NULL),
(20,20,'free','manual','2026-02-10',NULL,NULL,NULL,NULL,NULL,NULL,NULL),
(21,21,'free','manual','2026-02-10',NULL,NULL,NULL,NULL,NULL,NULL,NULL);
UNLOCK TABLES;

DROP TABLE IF EXISTS `planes`;
CREATE TABLE `planes` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `codigo` enum('mensual','semestral','anual') NOT NULL,
  `nombre` varchar(100) NOT NULL,
  `paypal_product_id` varchar(64) NOT NULL,
  `paypal_plan_id` varchar(64) NOT NULL,
  `moneda` varchar(3) NOT NULL,
  `precio` decimal(10,2) NOT NULL,
  `intervalo_unidad` varchar(16) NOT NULL,
  `intervalo_conteo` int(11) NOT NULL,
  `activo` tinyint(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (`id`),
  UNIQUE KEY `codigo` (`codigo`),
  UNIQUE KEY `paypal_plan_id` (`paypal_plan_id`),
  KEY `ix_planes_id` (`id`),
  KEY `ix_planes_paypal_plan_id` (`paypal_plan_id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;

LOCK TABLES `planes` WRITE;
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
