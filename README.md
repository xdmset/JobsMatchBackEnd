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

mysql -u root -p jobsmatch < respaldo_jobsmatch_2026-04-04.sql
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

Variables de entorno para PayPal Subscriptions:

```env
PAYPAL_CLIENT_ID=tu_client_id
PAYPAL_SECRET=tu_secret
PAYPAL_BASE_URL=https://api-m.sandbox.paypal.com
PAYPAL_WEBHOOK_ID=tu_webhook_id
PAYPAL_WEB_RETURN_URL=http://localhost:3000/payments/paypal/success
PAYPAL_WEB_CANCEL_URL=http://localhost:3000/payments/paypal/cancel
PAYPAL_CURRENCY=MXN
PAYPAL_STUDENT_PRODUCT_NAME=JOBMATCH Premium Estudiante
PAYPAL_STUDENT_PRODUCT_DESCRIPTION=Suscripciones premium para estudiantes
PAYPAL_COMPANY_PRODUCT_NAME=JOBMATCH Premium Empresa
PAYPAL_COMPANY_PRODUCT_DESCRIPTION=Suscripciones premium para empresas
PAYPAL_STUDENT_MONTHLY_PRICE=199.00
PAYPAL_STUDENT_SEMIANNUAL_PRICE=999.00
PAYPAL_STUDENT_ANNUAL_PRICE=1799.00
PAYPAL_COMPANY_MONTHLY_PRICE=499.00
PAYPAL_COMPANY_SEMIANNUAL_PRICE=2499.00
PAYPAL_COMPANY_ANNUAL_PRICE=4499.00

STUDENT_FREE_DAILY_SWIPES=10
STUDENT_PREMIUM_DAILY_SWIPES=1000
STUDENT_FREE_VIEW_HISTORY_LIMIT=15
STUDENT_PREMIUM_VIEW_HISTORY_LIMIT=0
STUDENT_FREE_MATCH_HISTORY_LIMIT=10
STUDENT_PREMIUM_MATCH_HISTORY_LIMIT=0

COMPANY_FREE_ACTIVE_VACANCIES=5
COMPANY_PREMIUM_ACTIVE_VACANCIES=50

ROADMAP_AI_MODE=heuristic
ROADMAP_AI_API_KEY=
ROADMAP_AI_MODEL=gpt-4o-mini
ROADMAP_AI_BASE_URL=https://api.openai.com/v1/chat/completions
ROADMAP_AI_TIMEOUT_SECONDS=30
```

Variables de entorno para roadmap de mejora por retroalimentacion:

```env
ROADMAP_AI_MODE=heuristic
ROADMAP_AI_API_KEY=
ROADMAP_AI_MODEL=gpt-4o-mini
ROADMAP_AI_BASE_URL=https://api.openai.com/v1/chat/completions
ROADMAP_AI_TIMEOUT_SECONDS=30
```

Notas:

- `ROADMAP_AI_MODE=heuristic` genera el roadmap localmente sin proveedor externo.
- `ROADMAP_AI_MODE=openai` habilita la generacion con proveedor externo y requiere `ROADMAP_AI_API_KEY`.
- Si la generacion falla, la retroalimentacion sigue guardandose y el endpoint respondera `roadmap_estado="error"`.

Modelo de suscripciones:

- Cada usuario nuevo recibe automaticamente una suscripcion `free` segun su rol: `free_estudiante` o `free_empresa`.
- Las suscripciones `premium` de PayPal se separan por rol y periodicidad.
- Catalogo premium soportado:
  - `premium_estudiante_mensual`
  - `premium_estudiante_semestral`
  - `premium_estudiante_anual`
  - `premium_empresa_mensual`
  - `premium_empresa_semestral`
  - `premium_empresa_anual`
- `usuarios.es_premium` se sincroniza desde las suscripciones activas.
- `GET /api/v1/user/me` recalcula `es_premium` antes de responder.
- `POST /api/v1/user/premium/sync` permite a un admin resincronizar todos los usuarios.

Flujo recomendado para PayPal Subscriptions:

1. Ejecuta `POST /api/v1/payments/paypal/bootstrap` con un admin para crear dos productos de PayPal:
   - Premium Estudiante
   - Premium Empresa
2. El frontend consulta:
   - `GET /api/v1/payments/paypal/plans` para catalogo completo
   - `GET /api/v1/payments/paypal/plans/me` para mostrar solo los planes del rol autenticado
3. El usuario autenticado inicia su alta con `POST /api/v1/payments/paypal/subscriptions`.
4. El frontend redirige al `approve_url` devuelto por PayPal.
5. Al volver a tu frontend, llama `POST /api/v1/payments/paypal/subscriptions/{paypal_subscription_id}/sync`.
6. Configura el webhook de PayPal apuntando a `POST /api/v1/payments/paypal/webhook`.

El endpoint `POST /api/v1/payments/paypal/subscriptions` acepta `return_url` y `cancel_url`, lo que permite usar el mismo backend para:

- Web: `https://jobmatch.com.mx/payments/paypal/success`
- Flutter: `https://jobmatch.com.mx/payments/paypal/mobile-success` o una ruta que redirija a deep link/app link

Ejemplo de creacion de suscripcion:

```json
{
  "billing_cycle": "mensual",
  "return_url": "https://jobmatch.com.mx/payments/paypal/success",
  "cancel_url": "https://jobmatch.com.mx/payments/paypal/cancel"
}
```

El backend resuelve automaticamente el plan correcto segun el rol autenticado:

- estudiante + `mensual` -> `premium_estudiante_mensual`
- empresa + `mensual` -> `premium_empresa_mensual`

Guia de implementacion frontend:

- React y Flutter: [PAYPAL_REACT_FLUTTER_GUIDE.md]

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

- `GET /api/v1/media/estudiantes/{usuario_id}/cv` requiere autenticacion del propio estudiante, empresa o admin.
- `POST /api/v1/auth/jwt/logout` es stateless: el cliente debe descartar ambos tokens.

## Roadmap de mejora por rechazo

Cuando una empresa rechaza una postulacion usando `PUT /api/v1/postulaciones/{postulacion_id}/estado` con `feedback`, el backend:

1. guarda o actualiza la retroalimentacion;
2. genera un roadmap de mejora para el estudiante usando:
   - `campos_mejora`
   - `sugerencias_perfil`
   - contexto de `perfil_estudiante`
   - contexto de la `vacante`
3. expone ese roadmap en `GET /api/v1/retroalimentacion/postulacion/{postulacion_id}`.

Campos nuevos devueltos por retroalimentacion:

- `roadmap_estado`: `pendiente`, `generado` o `error`
- `roadmap_generado_en`
- `roadmap`

Ejemplo de respuesta:

```json
{
  "id": 1,
  "postulacion_id": 42,
  "campos_mejora": "Mejorar SQL",
  "sugerencias_perfil": "Agregar proyectos backend",
  "fecha_envio": "2026-04-07T10:00:00Z",
  "roadmap_estado": "generado",
  "roadmap_generado_en": "2026-04-07T10:00:02Z",
  "roadmap": {
    "habilidades": [
      "SQL aplicado a vacantes reales",
      "Desarrollo de proyectos backend demostrables"
    ],
    "acciones": [
      "Resolver 15 ejercicios de consultas con JOIN, GROUP BY y subconsultas.",
      "Construir una base de datos pequena para un proyecto personal y documentar 10 consultas utiles.",
      "Construir un proyecto backend pequeno con autenticacion, persistencia y documentacion.",
      "Agregar README tecnico con arquitectura, endpoints y decisiones de diseno."
    ],
    "recursos": [
      "SQLBolt",
      "Mode SQL Tutorial",
      "LeetCode SQL",
      "GitHub",
      "Postman"
    ],
    "tiempo_estimado": "3 semanas",
    "prioridad": "Alta",
    "roadmap_detallado": [
      {
        "semana": "Semana 1",
        "objetivo": "Cerrar brechas tecnicas principales detectadas en la retroalimentacion.",
        "tareas": [
          "Resolver 15 ejercicios de consultas con JOIN, GROUP BY y subconsultas.",
          "Construir una base de datos pequena para un proyecto personal y documentar 10 consultas utiles.",
          "Construir un proyecto backend pequeno con autenticacion, persistencia y documentacion."
        ]
      }
    ]
  }
}
```

Regeneracion manual:

```text
POST /api/v1/retroalimentacion/postulacion/{postulacion_id}/generar-roadmap
```

## Matriz de acceso por rol

| Endpoint / Recurso | Publico | Estudiante | Empresa | Admin |
| --- | --- | --- | --- | --- |
| `POST /api/v1/auth/jwt/login` | Si | Si | Si | Si |
| `POST /api/v1/auth/jwt/refresh` | Si | Si | Si | Si |
| `POST /api/v1/auth/jwt/logout` | No | Si | Si | Si |
| `POST /api/v1/user/` | Si | Si | Si | Si |
| `GET /api/v1/user/` | No | No | No | Si |
| `GET /api/v1/user/me` | No | Si | Si | Si |
| `POST /api/v1/user/premium/sync` | No | No | No | Si |
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
| `GET /api/v1/media/estudiantes/{usuario_id}/cv` | No | Solo propio recurso | Si | Si |
| `POST/DELETE /api/v1/media/estudiantes/{usuario_id}/cv` | No | Solo propio recurso | No | Si |
| `GET /api/v1/media/empresas/{usuario_id}/foto` | Si | Si | Si | Si |
| `POST/DELETE /api/v1/media/empresas/{usuario_id}/foto` | No | No | Solo propio recurso | Si |
| `POST /api/v1/swipes/{estudiante_id}` | No | Solo su propio `estudiante_id` | No | Si |
| `GET /api/v1/swipes/{estudiante_id}/vacantes` | No | Solo su propio `estudiante_id` | No | Si |
| `POST /api/v1/swipes/empresa/{empresa_id}` | No | No | Solo su propio `empresa_id` | Si |
| `GET /api/v1/swipes/empresa/{empresa_id}/candidatos?vacante_id=*` | No | No | Solo su propio `empresa_id` | Si |
| `GET /api/v1/matches/estudiante/{estudiante_id}` | No | Solo su propio `estudiante_id` | No | Si |
| `POST /api/v1/postulaciones/web` | No | Solo su propia postulacion | No | Si |
| `GET /api/v1/postulaciones/empresa/{empresa_id}` | No | No | Solo su propia empresa | Si |
| `PUT /api/v1/postulaciones/{postulacion_id}/estado` | No | No | Solo postulaciones de su empresa | Si |
| `GET /api/v1/retroalimentacion/{retroalimentacion_id}` | No | Solo si pertenece a su postulacion | Solo si pertenece a su empresa | Si |
| `GET /api/v1/retroalimentacion/postulacion/{postulacion_id}` | No | Solo si pertenece a su postulacion | Solo si pertenece a su empresa | Si |
| `POST /api/v1/retroalimentacion/postulacion/{postulacion_id}/generar-roadmap` | No | Solo si pertenece a su postulacion | Solo si pertenece a su empresa | Si |
| `POST/PUT/DELETE /api/v1/retroalimentacion/*` | No | No | Solo sobre postulaciones de su empresa | Si |
| `GET /api/v1/suscripciones/usuario/{usuario_id}` | No | Solo propias | Solo propias | Si |
| `GET /api/v1/suscripciones/usuario/{usuario_id}/actual` | No | Solo propia | Solo propia | Si |
| `GET /api/v1/suscripciones/` y `GET /api/v1/suscripciones/{suscripcion_id}` | No | No | No | Si |
| `POST/PUT/DELETE /api/v1/suscripciones/*` | No | No | No | Si |
| `GET /api/v1/payments/paypal/plans` | Si | Si | Si | Si |
| `GET /api/v1/payments/paypal/plans/me` | No | Si | Si | Si |
| `POST /api/v1/payments/paypal/bootstrap` | No | No | No | Si |
| `POST /api/v1/payments/paypal/subscriptions` | No | Si | Si | Si |
| `POST /api/v1/payments/paypal/subscriptions/{paypal_subscription_id}/sync` | No | Solo propia | Solo propia | Si |
| `POST /api/v1/payments/paypal/subscriptions/{paypal_subscription_id}/cancel` | No | Solo propia | Solo propia | Si |
| `POST /api/v1/payments/paypal/webhook` | Si | Si | Si | Si |

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
- `PAYPAL_CLIENT_ID`
- `PAYPAL_SECRET`
- `PAYPAL_BASE_URL`
- `PAYPAL_WEBHOOK_ID`
- `PAYPAL_WEB_RETURN_URL`
- `PAYPAL_WEB_CANCEL_URL`
- `PAYPAL_CURRENCY`
- `PAYPAL_STUDENT_*`
- `PAYPAL_COMPANY_*`
- `STUDENT_*`
- `COMPANY_*`
- `ROADMAP_AI_*`

Ejemplo:

```env
DATABASE_URL=mysql+pymysql://jobmatch:change-me@mysql:3306/jobmatch_db
SECRET_KEY=replace-with-a-32-byte-secret
REFRESH_TOKEN_SECRET=replace-with-another-32-byte-secret
CORS_ORIGINS=https://api.tudominio.com,https://app.tudominio.com
MINIO_ENDPOINT=minio:9000
MINIO_PUBLIC_ENDPOINT=https://files.tudominio.com
PAYPAL_BASE_URL=https://api-m.paypal.com
PAYPAL_WEBHOOK_ID=tu_webhook_id_live
PAYPAL_CURRENCY=MXN
PAYPAL_WEB_RETURN_URL=https://jobmatch.com.mx/payments/paypal/success
PAYPAL_WEB_CANCEL_URL=https://jobmatch.com.mx/payments/paypal/cancel
ROADMAP_AI_MODE=heuristic
ROADMAP_AI_MODEL=gpt-4o-mini
ROADMAP_AI_BASE_URL=https://api.openai.com/v1/chat/completions
ROADMAP_AI_TIMEOUT_SECONDS=30
```

### Operacion de suscripciones

Bootstrap de planes PayPal:

```bash
curl -X POST https://api.jobmatch.com.mx/api/v1/payments/paypal/bootstrap \
  -H "Authorization: Bearer TU_TOKEN_ADMIN"
```

Sincronizacion global de premium:

```bash
curl -X POST https://api.jobmatch.com.mx/api/v1/user/premium/sync \
  -H "Authorization: Bearer TU_TOKEN_ADMIN"
```

Consulta de plan actual de un usuario:

```bash
curl https://api.jobmatch.com.mx/api/v1/suscripciones/usuario/123/actual \
  -H "Authorization: Bearer TU_TOKEN"
```

Consulta de planes PayPal para el rol autenticado:

```bash
curl https://api.jobmatch.com.mx/api/v1/payments/paypal/plans/me \
  -H "Authorization: Bearer TU_TOKEN"
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

El archivo `respaldo_jobsmatch_2026-04-04.sql` crea un admin con:

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
