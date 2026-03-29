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
- Estudiante: solo puede modificar su propio perfil, CV, foto, historial de vistas, swipes y postulaciones web.
- Empresa: solo puede modificar su propio perfil, foto, vacantes, swipes de empresa, postulaciones y retroalimentacion asociada a sus vacantes.
- Admin o duenio del recurso: eliminacion de usuario propio y lectura de recursos privados segun corresponda.

Notas:

- `GET /api/v1/media/estudiantes/{usuario_id}/cv` requiere autenticacion del propio estudiante, empresa o admin.
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
| `POST /api/v1/vacante/{vacante_id}/view` | No | Si | No | Si |
| `GET /api/v1/vacante/historial/estudiante/{estudiante_id}` | No | Solo su propio `estudiante_id` | No | Si |
| `GET /api/v1/vacante/historial/empresa/{empresa_id}` | No | No | Solo su propio `empresa_id` | Si |
| `POST /api/v1/vacante/{empresa_id}` | No | No | Solo propia empresa | Si |
| `PUT/DELETE /api/v1/vacante/{vacante_id}` | No | No | Solo vacantes propias | Si |
| `GET /api/v1/perfil_estudiante/{usuario_id}` | Si | Si | Si | Si |
| `POST/PUT/DELETE /api/v1/perfil_estudiante/{usuario_id}` | No | Solo propio perfil | No | Si |
| `GET /api/v1/perfil_empresa/{user_id}` | Si | Si | Si | Si |
| `POST/PUT/DELETE /api/v1/perfil_empresa/{user_id}` | No | No | Solo propio perfil | Si |
| `GET /api/v1/media/estudiantes/{usuario_id}/foto` | Si | Si | Si | Si |
| `POST/DELETE /api/v1/media/estudiantes/{usuario_id}/foto` | No | Solo propio recurso | No | Si |
| `GET /api/v1/media/estudiantes/{usuario_id}/cv` | No | Solo propio recurso | Si | Si |
| `POST/DELETE /api/v1/media/estudiantes/{usuario_id}/cv` | No | Solo propio recurso | No | Si |
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

## Perfiles y fecha de nacimiento

- `perfil_estudiante.fecha_nacimiento` es obligatoria al crear o actualizar un alumno.
- `perfil_empresa` no incluye `fecha_nacimiento`.
- La edad debe calcularse en frontend a partir de la fecha devuelta por la API.

Ejemplo minimo de alta de alumno:

```json
{
  "email": "alumno@test.com",
  "password": "secret123",
  "rol_id": 2,
  "perfil_estudiante": {
    "nombre_completo": "Alumno Demo",
    "institucion_educativa": "UTT",
    "nivel_academico": "Licenciatura",
    "fecha_nacimiento": "2002-09-18"
  }
}
```

## Historial de vacantes

La API ahora separa dos conceptos:

- visualizacion: el alumno abrio o reviso una vacante.
- swipe: el alumno o la empresa tomo una decision explicita de interes.

Endpoints nuevos:

```text
POST /api/v1/vacante/{vacante_id}/view
GET /api/v1/vacante/historial/estudiante/{estudiante_id}
GET /api/v1/vacante/historial/empresa/{empresa_id}
```

### Como funciona

Para alumno:

1. El frontend muestra el listado de vacantes.
2. Cuando el alumno entra al detalle de una vacante, debe llamar `POST /api/v1/vacante/{vacante_id}/view`.
3. Si el alumno da like o dislike, se sigue usando `POST /api/v1/swipes/{estudiante_id}`.
4. Para mostrar historial o favoritos vistos, se consulta `GET /api/v1/vacante/historial/estudiante/{estudiante_id}`.

Para empresa:

1. La empresa sigue usando `POST /api/v1/swipes/empresa/{empresa_id}` para expresar interes en alumnos.
2. Para analitica de sus vacantes, consulta `GET /api/v1/vacante/historial/empresa/{empresa_id}`.
3. Ese endpoint devuelve por vacante los totales de vistas, alumnos que la vieron, likes de alumnos, likes emitidos por la empresa y matches.

### Uso recomendado en frontend

- No dispares `view` solo por renderizar una card en el listado.
- Dispara `view` al abrir el detalle real de la vacante.
- Usa el historial del alumno para construir pantallas como `Vistas recientemente`, `Favoritas` o `Revisadas varias veces`.
- Usa el historial de empresa como dashboard o tabla de rendimiento por vacante.

### Ejemplos de respuesta

`POST /api/v1/vacante/1/view`

```json
{
  "vacante_id": 1,
  "estudiante_id": 12,
  "primera_visualizacion": "2026-03-28T18:05:12Z",
  "ultima_visualizacion": "2026-03-28T18:05:12Z",
  "total_visualizaciones": 1
}
```

`GET /api/v1/vacante/historial/estudiante/12`

```json
[
  {
    "id": 1,
    "empresa_id": 7,
    "titulo": "Backend Developer Python",
    "descripcion": "Desarrollo de APIs con FastAPI",
    "requisitos": "Conocimientos en SQL y Python",
    "tipo_contrato": null,
    "modalidad": "remoto",
    "ubicacion": "Tijuana, BC",
    "sueldo_minimo": 15000.0,
    "sueldo_maximo": 20000.0,
    "moneda": "MXN",
    "estado": "activa",
    "fecha_publicacion": "2026-03-20T14:30:00Z",
    "primera_visualizacion": "2026-03-28T17:50:00Z",
    "ultima_visualizacion": "2026-03-28T18:05:12Z",
    "total_visualizaciones": 3,
    "le_dio_like": true,
    "fecha_like": "2026-03-28T18:06:10Z"
  }
]
```

`GET /api/v1/vacante/historial/empresa/7`

```json
[
  {
    "id": 1,
    "empresa_id": 7,
    "titulo": "Backend Developer Python",
    "descripcion": "Desarrollo de APIs con FastAPI",
    "requisitos": "Conocimientos en SQL y Python",
    "tipo_contrato": null,
    "modalidad": "remoto",
    "ubicacion": "Tijuana, BC",
    "sueldo_minimo": 15000.0,
    "sueldo_maximo": 20000.0,
    "moneda": "MXN",
    "estado": "activa",
    "fecha_publicacion": "2026-03-20T14:30:00Z",
    "total_visualizaciones": 18,
    "total_estudiantes_que_vieron": 9,
    "total_likes_estudiantes": 4,
    "total_likes_empresa": 3,
    "total_matches": 2,
    "ultima_visualizacion": "2026-03-28T18:05:12Z",
    "ultimo_like_estudiante": "2026-03-28T18:06:10Z",
    "ultimo_like_empresa": "2026-03-28T18:10:45Z"
  }
]
```

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
MINIO_ENDPOINT=minio:9000
MINIO_PUBLIC_ENDPOINT=https://files.tudominio.com
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

### Usuario admin del respaldo

El archivo `respaldo_jobsmatch_2026-02-10.sql` crea un admin con:

- Email: `admin@test.com`
- Password (antes del hash): `AdminJobmatch2026!`

Si necesitas cambiar la contraseña, puedes:

1. Iniciar sesión (si la API está arriba) y usar la API de usuarios para actualizarla.
2. Ejecutar manualmente un `UPDATE usuarios SET password_hash = '<nuevo-hash>' WHERE email = 'admin@test.com';` (usa `app.core.security.get_password_hash` desde una shell Python para generar el hash).

Siempre rota la clave después de publicar el backup en un entorno público.

### Pasar de develop a main

1. Asegura que staging (`develop`) ya está estable: tests + deploy + health check bajo HTTPS.
2. Verifica que los secrets `_PROD` existan y que el dominio apunta al VPS con certificados válidos.
3. Merge o push directo a `main`; el workflow usará los secrets `PROD` y la imagen GHCR correspondiente.
4. Confirma que el job termina exitoso, que `docker ps` en el VPS refleja la nueva imagen y que `https://api.jobmatch.com.mx/health` responde `ok`.
5. Si necesitas retroceder rápida, usa `./deploy/rollback.sh` en el VPS antes de volver a lanzar el push en `main`.
