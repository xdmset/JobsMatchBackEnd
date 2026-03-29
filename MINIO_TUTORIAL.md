# MinIO en JOBMATCH

## 1. Que hace esta integracion

La API ahora puede:

- Subir foto de perfil de estudiante
- Subir CV de estudiante
- Subir foto de perfil de empresa
- Guardar en base de datos la `storage_key`
- Generar una URL firmada temporal para descargar o visualizar el archivo

## 2. Variables de entorno

Agrega estas variables a tu `.env`:

```env
DATABASE_URL=mysql+pymysql://mysql:123Tamarindo@localhost:3306/jobmatch_db
SECRET_KEY=Amarillo,Amarillo,Platano
ACCESS_TOKEN_EXPIRE_MINUTES=30
MINIO_ENDPOINT=localhost:9000
MINIO_PUBLIC_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=admin
MINIO_SECRET_KEY=password123
MINIO_BUCKET_NAME=uploads
USE_SSL=False
MEDIA_URL_EXPIRATION_SECONDS=3600
MAX_IMAGE_UPLOAD_BYTES=5242880
MAX_DOCUMENT_UPLOAD_BYTES=10485760
```

Si ejecutas la API fuera de Docker, estos valores locales siguen siendo correctos:

```env
DATABASE_URL=mysql+pymysql://mysql:123Tamarindo@localhost:3306/jobmatch_db
MINIO_ENDPOINT=localhost:9000
MINIO_PUBLIC_ENDPOINT=localhost:9000
```

## 3. Levantar servicios

Instala dependencias:

```bash
pip install -r requirements.txt
```

Levanta API + MinIO:

```bash
docker compose up --build
```

En Docker, el compose ya levanta:

- `mysql`
- `minio`
- `api`

Y dentro de la red interna usa:

- `DATABASE_URL=mysql+pymysql://mysql:123Tamarindo@mysql:3306/jobmatch_db`
- `MINIO_ENDPOINT=minio:9000`
- `MINIO_PUBLIC_ENDPOINT=localhost:9000`

Asi no tienes que editar el `.env` para cambiar entre local y Docker.

Servicios expuestos en tu maquina:

- API backend: `http://localhost:8000`
- MySQL: `localhost:3306`
- API S3 de MinIO: `http://localhost:9000`
- Consola MinIO: `http://localhost:9001`

Credenciales por defecto:

- usuario: `admin`
- password: `password123`

Credenciales del MySQL del compose:

- host: `localhost`
- puerto: `3306`
- database: `jobmatch_db`
- user: `mysql`
- password: `123Tamarindo`

## 4. Migraciones

Con el stack levantado, aplica migraciones:

```bash
docker compose exec api alembic upgrade head
```

Esto agrega columnas para guardar:

- `cv_storage_key`
- `foto_perfil_storage_key`

## 5. Flujo correcto de uso

1. Levantar `mysql`, `minio` y `api`
2. Ejecutar migraciones
3. Crear usuario
4. Crear perfil de estudiante o empresa
5. Subir archivo al endpoint `/api/v1/media/...`
6. Guardar la `storage_key` en la DB automaticamente
7. Pedir una URL firmada temporal con `GET /api/v1/media/...`

## 6. Endpoints disponibles

### Estudiante

- `POST /api/v1/media/estudiantes/{usuario_id}/foto`
- `GET /api/v1/media/estudiantes/{usuario_id}/foto`
- `DELETE /api/v1/media/estudiantes/{usuario_id}/foto`
- `POST /api/v1/media/estudiantes/{usuario_id}/cv`
- `GET /api/v1/media/estudiantes/{usuario_id}/cv`
- `DELETE /api/v1/media/estudiantes/{usuario_id}/cv`

### Empresa

- `POST /api/v1/media/empresas/{usuario_id}/foto`
- `GET /api/v1/media/empresas/{usuario_id}/foto`
- `DELETE /api/v1/media/empresas/{usuario_id}/foto`

## 7. Ejemplos con curl

Subir foto de estudiante:

```bash
curl -X POST "http://localhost:8000/api/v1/media/estudiantes/2/foto" \
  -F "file=@/ruta/a/foto.jpg"
```

Subir CV:

```bash
curl -X POST "http://localhost:8000/api/v1/media/estudiantes/2/cv" \
  -F "file=@/ruta/a/cv.pdf"
```

Obtener URL firmada del CV:

```bash
curl "http://localhost:8000/api/v1/media/estudiantes/2/cv"
```

Subir foto de empresa:

```bash
curl -X POST "http://localhost:8000/api/v1/media/empresas/3/foto" \
  -F "file=@/ruta/a/logo.png"
```

## 8. Detalles importantes

- Las imagenes aceptadas son `jpg`, `png`, `webp`
- El CV acepta solo `pdf`
- La URL firmada expira segun `MEDIA_URL_EXPIRATION_SECONDS`
- No guardes URLs firmadas permanentemente en frontend o DB
- La DB guarda la clave del objeto, no una URL publica fija

## 9. Problemas comunes

### La API arranca pero MinIO no responde

Revisa que `MINIO_ENDPOINT` sea accesible desde donde corre la API.

Si corres `uvicorn` localmente, `MINIO_ENDPOINT` debe ser `localhost:9000`, no `minio:9000`.

### La API en Docker no conecta a MySQL

Dentro del contenedor, la API debe usar `mysql` como hostname, no `localhost`.

Este proyecto ya quedo configurado para eso.

### La URL firmada apunta a un host o esquema incorrecto

Ajusta `MINIO_PUBLIC_ENDPOINT`.

Ejemplo:

- API en Docker: `MINIO_ENDPOINT=minio:9000`
- Navegador local: `MINIO_PUBLIC_ENDPOINT=http://localhost:9000`
- VPS con HTTPS: `MINIO_PUBLIC_ENDPOINT=https://files.tudominio.com`

### Error por bucket inexistente

La app intenta crearlo al iniciar. Si falla, revisa credenciales y conectividad.
