/*M!999999\- enable the sandbox mode */ 
-- MariaDB dump 10.19  Distrib 10.11.15-MariaDB, for Linux (x86_64)
--
-- Host: localhost    Database: jobsmatch
-- ------------------------------------------------------
-- Server version	10.11.15-MariaDB

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

--
-- Table structure for table `alembic_version`
--

DROP TABLE IF EXISTS `alembic_version`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `alembic_version` (
  `version_num` varchar(32) NOT NULL,
  PRIMARY KEY (`version_num`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `alembic_version`
--

LOCK TABLES `alembic_version` WRITE;
/*!40000 ALTER TABLE `alembic_version` DISABLE KEYS */;
INSERT INTO `alembic_version` VALUES
('01cf01c545bd');
/*!40000 ALTER TABLE `alembic_version` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `interacciones_swipe`
--

DROP TABLE IF EXISTS `interacciones_swipe`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `interacciones_swipe` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `estudiante_id` int(11) DEFAULT NULL,
  `vacante_id` int(11) DEFAULT NULL,
  `interes_estudiante` tinyint(1) DEFAULT NULL,
  `fecha` datetime DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  KEY `estudiante_id` (`estudiante_id`),
  KEY `vacante_id` (`vacante_id`),
  KEY `ix_interacciones_swipe_id` (`id`),
  CONSTRAINT `interacciones_swipe_ibfk_1` FOREIGN KEY (`estudiante_id`) REFERENCES `perfiles_estudiantes` (`usuario_id`),
  CONSTRAINT `interacciones_swipe_ibfk_2` FOREIGN KEY (`vacante_id`) REFERENCES `vacantes` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `interacciones_swipe`
--

LOCK TABLES `interacciones_swipe` WRITE;
/*!40000 ALTER TABLE `interacciones_swipe` DISABLE KEYS */;
INSERT INTO `interacciones_swipe` VALUES
(1,1,1,1,'2026-02-09 19:07:39'),
(2,1,1,1,'2026-02-09 19:30:07'),
(3,1,2,1,'2026-02-10 13:35:30'),
(4,1,3,0,'2026-02-10 13:35:30'),
(5,1,1,1,'2026-02-10 13:35:30'),
(6,1,2,0,'2026-02-10 13:35:30'),
(7,1,3,1,'2026-02-10 13:35:30'),
(8,1,1,0,'2026-02-10 13:35:30'),
(9,1,2,1,'2026-02-10 13:35:30'),
(10,1,3,0,'2026-02-10 13:35:30'),
(11,1,1,1,'2026-02-10 13:36:17'),
(12,1,1,1,'2026-02-10 13:36:42'),
(15,3,2,1,'2026-02-10 18:43:51');
/*!40000 ALTER TABLE `interacciones_swipe` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `matches`
--

DROP TABLE IF EXISTS `matches`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `matches` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `estudiante_id` int(11) DEFAULT NULL,
  `vacante_id` int(11) DEFAULT NULL,
  `fecha_match` datetime DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  KEY `estudiante_id` (`estudiante_id`),
  KEY `vacante_id` (`vacante_id`),
  KEY `ix_matches_id` (`id`),
  CONSTRAINT `matches_ibfk_1` FOREIGN KEY (`estudiante_id`) REFERENCES `perfiles_estudiantes` (`usuario_id`),
  CONSTRAINT `matches_ibfk_2` FOREIGN KEY (`vacante_id`) REFERENCES `vacantes` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `matches`
--

LOCK TABLES `matches` WRITE;
/*!40000 ALTER TABLE `matches` DISABLE KEYS */;
INSERT INTO `matches` VALUES
(1,1,1,'2026-02-09 19:07:48'),
(2,1,1,'2026-02-09 19:30:07'),
(3,1,1,'2026-02-10 13:36:17'),
(4,1,1,'2026-02-10 13:36:42'),
(5,3,2,'2026-02-10 18:43:51');
/*!40000 ALTER TABLE `matches` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `perfiles_empresas`
--

DROP TABLE IF EXISTS `perfiles_empresas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `perfiles_empresas` (
  `usuario_id` int(11) NOT NULL,
  `nombre_comercial` varchar(255) NOT NULL,
  `sector` varchar(255) DEFAULT NULL,
  `descripcion` text DEFAULT NULL,
  `sitio_web` varchar(255) DEFAULT NULL,
  `ubicacion_sede` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`usuario_id`),
  CONSTRAINT `perfiles_empresas_ibfk_1` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `perfiles_empresas`
--

LOCK TABLES `perfiles_empresas` WRITE;
/*!40000 ALTER TABLE `perfiles_empresas` DISABLE KEYS */;
INSERT INTO `perfiles_empresas` VALUES
(2,'Tech Solutions','Tecnología','Empresa de desarrollo de software',NULL,'Tijuana, BC');
/*!40000 ALTER TABLE `perfiles_empresas` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `perfiles_estudiantes`
--

DROP TABLE IF EXISTS `perfiles_estudiantes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `perfiles_estudiantes` (
  `usuario_id` int(11) NOT NULL,
  `nombre_completo` varchar(255) DEFAULT NULL,
  `institucion_educativa` varchar(255) DEFAULT NULL,
  `nivel_academico` varchar(255) DEFAULT NULL,
  `biografia` text DEFAULT NULL,
  `habilidades` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`habilidades`)),
  `cv_url` varchar(255) DEFAULT NULL,
  `cv_tipo_archivo` varchar(255) DEFAULT NULL,
  `foto_perfil_url` varchar(255) DEFAULT NULL,
  `ubicacion` varchar(255) DEFAULT NULL,
  `modalidad_preferida` enum('remoto','presencial','hibrido') DEFAULT NULL,
  PRIMARY KEY (`usuario_id`),
  CONSTRAINT `perfiles_estudiantes_ibfk_1` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `perfiles_estudiantes`
--

LOCK TABLES `perfiles_estudiantes` WRITE;
/*!40000 ALTER TABLE `perfiles_estudiantes` DISABLE KEYS */;
INSERT INTO `perfiles_estudiantes` VALUES
(1,'Leonel Test','UTT','TSU','Desarrollador Backend Jr.','{\"python\": \"avanzado\", \"fastapi\": \"intermedio\"}',NULL,NULL,NULL,NULL,'remoto'),
(3,'Leonel Pro','IPN','Ingeniería','Desarrollador Senior buscando retos.','{\"python\": \"experto\", \"cloud\": \"avanzado\"}',NULL,NULL,NULL,NULL,'hibrido');
/*!40000 ALTER TABLE `perfiles_estudiantes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `postulaciones`
--

DROP TABLE IF EXISTS `postulaciones`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `postulaciones` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `match_id` int(11) DEFAULT NULL,
  `estado` enum('enviado','visto','en_proceso','rechazado') DEFAULT NULL,
  `fecha_actualizacion` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `match_id` (`match_id`),
  KEY `ix_postulaciones_id` (`id`),
  CONSTRAINT `postulaciones_ibfk_1` FOREIGN KEY (`match_id`) REFERENCES `matches` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `postulaciones`
--

LOCK TABLES `postulaciones` WRITE;
/*!40000 ALTER TABLE `postulaciones` DISABLE KEYS */;
INSERT INTO `postulaciones` VALUES
(1,1,'enviado',NULL),
(2,2,'enviado',NULL),
(3,3,'enviado',NULL),
(4,4,'enviado',NULL),
(5,5,'enviado',NULL);
/*!40000 ALTER TABLE `postulaciones` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `retroalimentacion`
--

DROP TABLE IF EXISTS `retroalimentacion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `retroalimentacion` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `postulacion_id` int(11) DEFAULT NULL,
  `campos_mejora` text DEFAULT NULL,
  `sugerencias_perfil` text DEFAULT NULL,
  `fecha_envio` datetime DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  KEY `postulacion_id` (`postulacion_id`),
  KEY `ix_retroalimentacion_id` (`id`),
  CONSTRAINT `retroalimentacion_ibfk_1` FOREIGN KEY (`postulacion_id`) REFERENCES `postulaciones` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `retroalimentacion`
--

LOCK TABLES `retroalimentacion` WRITE;
/*!40000 ALTER TABLE `retroalimentacion` DISABLE KEYS */;
/*!40000 ALTER TABLE `retroalimentacion` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `roles`
--

DROP TABLE IF EXISTS `roles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `roles` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `nombre` varchar(50) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `nombre` (`nombre`),
  KEY `ix_roles_id` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `roles`
--

LOCK TABLES `roles` WRITE;
/*!40000 ALTER TABLE `roles` DISABLE KEYS */;
INSERT INTO `roles` VALUES
(1,'admin'),
(3,'empresa'),
(2,'estudiante');
/*!40000 ALTER TABLE `roles` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `usuarios`
--

DROP TABLE IF EXISTS `usuarios`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `usuarios` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `rol_id` int(11) NOT NULL,
  `email` varchar(255) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `es_premium` tinyint(1) DEFAULT NULL,
  `fecha_registro` datetime DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_usuarios_email` (`email`),
  KEY `rol_id` (`rol_id`),
  KEY `ix_usuarios_id` (`id`),
  CONSTRAINT `usuarios_ibfk_1` FOREIGN KEY (`rol_id`) REFERENCES `roles` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `usuarios`
--

LOCK TABLES `usuarios` WRITE;
/*!40000 ALTER TABLE `usuarios` DISABLE KEYS */;
INSERT INTO `usuarios` VALUES
(1,2,'estudiante@test.com','$argon2id$v=19$m=65536,t=3,p=4$6mZ...your_hash',0,'2026-02-09 19:05:06'),
(2,3,'empresa@test.com','$argon2id$v=19$m=65536,t=3,p=4$6mZ...your_hash',1,'2026-02-09 19:06:34'),
(3,2,'estudiante_pro@test.com','hash_aqui',1,'2026-02-10 13:28:00');
/*!40000 ALTER TABLE `usuarios` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `vacantes`
--

DROP TABLE IF EXISTS `vacantes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
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
  `moneda` varchar(255) DEFAULT NULL,
  `estado` enum('activa','pausada','cerrada') DEFAULT NULL,
  `fecha_publicacion` datetime DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  KEY `empresa_id` (`empresa_id`),
  KEY `ix_vacantes_id` (`id`),
  CONSTRAINT `vacantes_ibfk_1` FOREIGN KEY (`empresa_id`) REFERENCES `perfiles_empresas` (`usuario_id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `vacantes`
--

LOCK TABLES `vacantes` WRITE;
/*!40000 ALTER TABLE `vacantes` DISABLE KEYS */;
INSERT INTO `vacantes` VALUES
(1,2,'Backend Developer Python','Desarrollo de APIs con FastAPI','Conocimientos en SQL y Python',NULL,'remoto',NULL,15000.00,20000.00,NULL,'activa','2026-02-09 19:07:31'),
(2,2,'Frontend Developer React','Desarrollo de interfaces web','React y CSS avanzado',NULL,'hibrido',NULL,12000.00,18000.00,NULL,'activa','2026-02-09 19:07:31'),
(3,2,'Ingeniero de Software','Vente a trabajar a Mty',NULL,NULL,'presencial','Monterrey, NL',18000.00,25000.00,NULL,'activa','2026-02-09 19:50:48'),
(4,2,'Arquitecto de Software','Diseño de sistemas distribuidos','10 años exp',NULL,'remoto','Global',80000.00,120000.00,NULL,'activa','2026-02-10 13:35:17');
/*!40000 ALTER TABLE `vacantes` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-02-10 21:26:02
