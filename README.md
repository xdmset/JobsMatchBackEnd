# JobsMatch API - Backend 🚀

Este es el núcleo del sistema JobsMatch, una plataforma diseñada para conectar estudiantes con empresas mediante una dinámica de "Match" basada en algoritmos de filtrado y un modelo de negocio Freemium.

## 🛠️ Tecnologías Utilizadas
* **Lenguaje:** Python 3.10+
* **Framework:** FastAPI
* **ORM:** SQLAlchemy
* **Base de Datos:** MariaDB / MySQL
* **Migraciones:** Alembic
* **Seguridad:** Argon2 (Hashing de contraseñas)

### 1. Preparar el Entorno Virtual

# Crear el entorno virtual
python3 -m venv venv

# Activar el entorno
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
2. Configuración de la Base de Datos (MariaDB)
Accede a tu consola de MariaDB y ejecuta:

SQL
CREATE DATABASE jobsmatch;
Configura tu conexión en el archivo app/core/config.py o mediante un archivo .env: DATABASE_URL=mysql+pymysql://usuario:password@localhost/jobsmatch

3. Migraciones de Base de Datos
Para crear la estructura de tablas automáticamente:

python3 -m alembic upgrade head
4. Carga de Datos de Prueba (Respaldo)
Si cuentas con el archivo de respaldo SQL, impórtalo para tener los roles, usuarios y vacantes iniciales:

mysql -u root -p jobsmatch < respaldo_jobsmatch.sql
🚀 Ejecución del Servidor
Para iniciar el servicio de desarrollo:

uvicorn app.main:app --reload
