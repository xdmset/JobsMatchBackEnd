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

## Calidad, CI/CD y seguridad

Instala herramientas de desarrollo:

```bash
pip install -r requirements.txt -r requirements-dev.txt
```

Comandos locales recomendados:

```bash
ruff check app tests
pytest --cov=app --cov-report=term-missing
bandit -q -r app -x tests
pip-audit --progress-spinner off
```

Pipeline de GitHub Actions:

- lint con `ruff`
- pruebas con `pytest` y cobertura
- escaneo SAST con `bandit`
- auditoria de dependencias con `pip-audit`
- build de imagen Docker

El workflow vive en `.github/workflows/ci.yml`.

## Autenticacion y autorizacion

La API usa JWT Bearer con dos tokens:

- `access_token`: vida corta para acceder a endpoints protegidos.
- `refresh_token`: vida mas larga para renovar sesion sin volver a pedir credenciales.

Variables de entorno relevantes:

```env
SECRET_KEY=super-secret
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_SECRET=super-secret-refresh
REFRESH_TOKEN_EXPIRE_DAYS=7
```

Flujo de autenticacion:

```text
POST /api/v1/auth/jwt/login
POST /api/v1/auth/jwt/refresh
POST /api/v1/auth/jwt/logout
```

Ejemplo de login:

```bash
curl -X POST http://localhost:8000/api/v1/auth/jwt/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "email=estudiante@test.com&password=tu_password"
```

Respuesta esperada:

```json
{
  "access_token": "jwt-access",
  "refresh_token": "jwt-refresh",
  "token_type": "bearer",
  "access_token_expires_in": 1800,
  "refresh_token_expires_in": 604800
}
```

Ejemplo de refresh:

```bash
curl -X POST http://localhost:8000/api/v1/auth/jwt/refresh \
  -H "Content-Type: application/json" \
  -d '{"refresh_token":"jwt-refresh"}'
```

Reglas de acceso:

- Publico: `POST /auth/jwt/login`, `POST /auth/jwt/refresh`, `POST /user`, `GET /vacante`, `GET /vacante/{id}`, `GET` de perfiles publicos y fotos publicas.
- Admin: gestion de roles, listado global de usuarios y administracion global de suscripciones.
- Estudiante: solo puede modificar su propio perfil, CV, foto, swipes y postulaciones web.
- Empresa: solo puede modificar su propio perfil, foto, vacantes, swipes de empresa, postulaciones y retroalimentacion asociada a sus vacantes.
- Admin o duenio del recurso: eliminacion de usuario propio y lectura de recursos privados segun corresponda.

Notas:

- `GET /api/v1/media/estudiantes/{usuario_id}/cv` requiere autenticacion del propio estudiante o admin.
- `POST /api/v1/auth/jwt/logout` es stateless: el cliente debe descartar ambos tokens.

## Matriz de acceso por rol

| Endpoint / Recurso | Publico | Estudiante | Empresa | Admin |
| --- | --- | --- | --- | --- |
| `POST /api/v1/auth/jwt/login` | Si | Si | Si | Si |
| `POST /api/v1/auth/jwt/refresh` | Si | Si | Si | Si |
| `POST /api/v1/auth/jwt/logout` | No | Si | Si | Si |
| `POST /api/v1/user/` | Si | Si | Si | Si |
| `GET /api/v1/user/` | No | No | No | Si |
| `DELETE /api/v1/user/{user_id}` | No | Solo propio usuario | Solo propio usuario | Si |
| `GET /api/v1/rol/` y `GET /api/v1/rol/{rol_id}` | No | No | No | Si |
| `POST/PUT/DELETE /api/v1/rol/*` | No | No | No | Si |
| `GET /api/v1/vacante/` y `GET /api/v1/vacante/{vacante_id}` | Si | Si | Si | Si |
| `POST /api/v1/vacante/{empresa_id}` | No | No | Solo propia empresa | Si |
| `PUT/DELETE /api/v1/vacante/{vacante_id}` | No | No | Solo vacantes propias | Si |
| `GET /api/v1/perfil_estudiante/{usuario_id}` | Si | Si | Si | Si |
| `POST/PUT/DELETE /api/v1/perfil_estudiante/{usuario_id}` | No | Solo propio perfil | No | Si |
| `GET /api/v1/perfil_empresa/{user_id}` | Si | Si | Si | Si |
| `POST/PUT/DELETE /api/v1/perfil_empresa/{user_id}` | No | No | Solo propio perfil | Si |
| `GET /api/v1/media/estudiantes/{usuario_id}/foto` | Si | Si | Si | Si |
| `POST/DELETE /api/v1/media/estudiantes/{usuario_id}/foto` | No | Solo propio recurso | No | Si |
| `POST/GET/DELETE /api/v1/media/estudiantes/{usuario_id}/cv` | No | Solo propio recurso | No | Si |
| `GET /api/v1/media/empresas/{usuario_id}/foto` | Si | Si | Si | Si |
| `POST/DELETE /api/v1/media/empresas/{usuario_id}/foto` | No | No | Solo propio recurso | Si |
| `POST /api/v1/swipes/{estudiante_id}` | No | Solo su propio `estudiante_id` | No | Si |
| `POST /api/v1/swipes/empresa/{empresa_id}` | No | No | Solo su propio `empresa_id` | Si |
| `POST /api/v1/postulaciones/web` | No | Solo su propia postulacion | No | Si |
| `GET /api/v1/postulaciones/empresa/{empresa_id}` | No | No | Solo su propia empresa | Si |
| `PUT /api/v1/postulaciones/{postulacion_id}/estado` | No | No | Solo postulaciones de su empresa | Si |
| `GET /api/v1/retroalimentacion/{retroalimentacion_id}` | No | Solo si pertenece a su postulacion | Solo si pertenece a su empresa | Si |
| `GET /api/v1/retroalimentacion/postulacion/{postulacion_id}` | No | Solo si pertenece a su postulacion | Solo si pertenece a su empresa | Si |
| `POST/PUT/DELETE /api/v1/retroalimentacion/*` | No | No | Solo sobre postulaciones de su empresa | Si |
| `GET /api/v1/suscripciones/usuario/{usuario_id}` | No | Solo propias | Solo propias | Si |
| `GET /api/v1/suscripciones/` y `GET /api/v1/suscripciones/{suscripcion_id}` | No | No | No | Si |
| `POST/PUT/DELETE /api/v1/suscripciones/*` | No | No | No | Si |

## Despliegue a VPS con Docker

Arquitectura esperada:

```text
push a develop/main -> GitHub Actions CD -> build y push a GHCR -> SSH al VPS -> docker compose -> backup MySQL -> deploy API
```

Archivos agregados para produccion:

- `docker-compose.prod.yml`
- `.env.prod.example`
- `deploy/deploy.sh`
- `deploy/rollback.sh`
- `deploy/backup_mysql.sh`
- `deploy/wait_for_health.sh`
- `.github/workflows/cd.yml`

### Certbot y HTTPS

1. Configura Nginx con el proxy hacia `http://127.0.0.1:8000`.
2. Instala `certbot` y su plugin (`sudo apt install certbot python3-certbot-nginx`).
3. Corre:

```bash
sudo certbot --nginx -d api.jobmatch.com.mx -d files.jobmatch.com.mx
```

4. Verifica que el cron generado renueve (`sudo certbot renew --dry-run`) y comprueba `/etc/letsencrypt/renewal/`.

### Bootstrap inicial en el VPS

1. Instala Docker Engine y Docker Compose plugin.
2. Crea el directorio del proyecto, por ejemplo `/opt/jobmatch`.
3. Copia `.env.prod.example` a `.env.prod` y ajusta secretos, dominios y credenciales.
4. Asegura que el puerto `8000` quede accesible solo desde tu reverse proxy o firewall.
5. Ejecuta el primer despliegue manual:

```bash
cd /opt/jobmatch
chmod +x deploy/*.sh
API_IMAGE=ghcr.io/TU_ORG/jobmatch-api:staging ./deploy/deploy.sh
```

### Secrets requeridos en GitHub Environments

Crea dos environments en GitHub:

- `staging`
- `production`

En cada uno define:

- `VPS_HOST`
- `VPS_PORT`
- `VPS_USER`
- `VPS_SSH_KEY`
- `APP_DIR`

Notas:

- `develop` despliega a `staging`
- `main` despliega a `production`
- la imagen se publica en `ghcr.io/<owner>/jobmatch-api`

### Variables importantes en `.env.prod`

- `DATABASE_URL`: debe apuntar al contenedor `mysql`
- `MYSQL_DATABASE`
- `MYSQL_USER`
- `MYSQL_PASSWORD`
- `MYSQL_ROOT_PASSWORD`
- `SECRET_KEY`
- `REFRESH_TOKEN_SECRET`
- `CORS_ORIGINS`
- `MINIO_*`

Ejemplo:

```env
DATABASE_URL=mysql+pymysql://jobmatch:change-me@mysql:3306/jobmatch_db
SECRET_KEY=replace-with-a-32-byte-secret
REFRESH_TOKEN_SECRET=replace-with-another-32-byte-secret
CORS_ORIGINS=https://api.tudominio.com,https://app.tudominio.com
```

### Operacion

Healthcheck:

```bash
curl http://TU_HOST:8000/health
```

Deploy manual:

```bash
API_IMAGE=ghcr.io/TU_ORG/jobmatch-api:production ./deploy/deploy.sh
```

Rollback:

```bash
./deploy/rollback.sh
```

Backup MySQL:

```bash
./deploy/backup_mysql.sh
```

### Pasar de develop a main

1. Asegura que staging (`develop`) ya está estable: tests + deploy + health check bajo HTTPS.
2. Verifica que los secrets `_PROD` existan y que el dominio apunta al VPS con certificados válidos.
3. Merge o push directo a `main`; el workflow usará los secrets `PROD` y la imagen GHCR correspondiente.
4. Confirma que el job termina exitoso, que `docker ps` en el VPS refleja la nueva imagen y que `https://api.jobmatch.com.mx/health` responde `ok`.
5. Si necesitas retroceder rápida, usa `./deploy/rollback.sh` en el VPS antes de volver a lanzar el push en `main`.
