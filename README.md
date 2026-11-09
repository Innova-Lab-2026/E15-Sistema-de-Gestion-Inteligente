# Sistema de Gestión Inteligente — TECBA (E15)

Orientación ciudadana para abrir una actividad comercial en CABA: el usuario describe qué quiere abrir y dónde, y el sistema le devuelve zonificación, requisitos, trámites y oficinas, con las fuentes oficiales citadas.

## Estructura del repositorio

```text
Backend/     API FastAPI + PostgreSQL (Docker)
  data/      datasets del equipo de datos (ver más abajo)
Frontend/    aplicación web (Vite + React)
.github/     CI: lint y tests del backend en cada push y PR
```

---

## Backend con Docker

### Requisitos

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (Windows / macOS) o Docker Engine con el plugin `compose` (Linux).
- Git.

No hace falta instalar Python ni PostgreSQL: todo corre en contenedores.

### Primera vez

Desde la carpeta `Backend/`:

```bash
cd Backend
cp .env.example .env            # Windows PowerShell: Copy-Item .env.example .env
docker compose --profile full up -d --build
```

Esto levanta dos contenedores:

| Contenedor | Qué es | Puerto en tu máquina |
|---|---|---|
| `tecba-db` | PostgreSQL 16 + PostGIS | `5432` |
| `tecba-api` | La API | `8000` |

Al arrancar, la API aplica las migraciones y, con `APP_ENV=local` (el valor de `.env.example`), carga el catálogo inicial. No hay que correr nada más.

### Comprobar que funciona

- Health: <http://localhost:8000/health> → `{"status":"ok"}`
- Base de datos conectada: <http://localhost:8000/ready> → `{"status":"ready"}`
- Documentación interactiva (Swagger): <http://localhost:8000/docs>

### Uso diario

Todos los comandos se corren desde `Backend/`.

| Para… | Comando |
|---|---|
| Levantar | `docker compose --profile full up -d` |
| Ver los logs de la API | `docker compose --profile full logs -f api` |
| Aplicar cambios de código (rebuild) | `docker compose --profile full up -d --build` |
| Detener (conserva los datos) | `docker compose --profile full stop` |
| Borrar contenedores (conserva los datos) | `docker compose --profile full down` |
| Empezar de cero (**borra la base**) | `docker compose --profile full down -v` |

> El código se copia dentro de la imagen: después de cambiar algo en `Backend/app/` hay que volver a correr el comando con `--build`.

### Problemas comunes

- **`port is already allocated`**: ya tenés algo usando el `5432` (otro PostgreSQL) o el `8000`. Cambiá el puerto del host al levantar:
  `DB_PORT=5433 API_PORT=8001 docker compose --profile full up -d`
  (PowerShell: `$env:DB_PORT=5433; $env:API_PORT=8001; docker compose --profile full up -d`).
- **El frontend no puede llamar a la API (error de CORS)**: el origen del front tiene que estar en `CORS_ORIGINS` de `Backend/.env`. Por defecto ya incluye `http://localhost:5173` (Vite) y `http://localhost:3000`.
- **Respuesta `429`**: es el límite de pedidos por minuto. Para pruebas locales podés poner `RATE_LIMIT_ENABLED=false` en `Backend/.env` y reiniciar con `docker compose --profile full up -d`.

### Configuración (`Backend/.env`)

- `.env` es personal y **nunca se sube al repo** (está en `.gitignore`). Si se agregan variables nuevas, se documentan en `.env.example`.
- `LLM_API_KEY` es opcional: sin clave, la interpretación de texto libre usa reglas locales.
- Detalle de cada variable: [Backend/documents/setup.md](Backend/documents/setup.md).

### Tests

En cada push y PR, GitHub Actions corre `ruff` y `pytest` automáticamente.

Para correrlos en local, con los contenedores levantados:

```bash
cd Backend
scripts/test.sh
```

Usan una base aparte (`tecba_test`) que se recrea en cada corrida; nunca tocan la de desarrollo.

> El script necesita `sh` y `docker run --network host`: funciona directo en Linux. En Docker Desktop (Windows / macOS) hay que activar *host networking* en la configuración de Docker; si no, alcanza con el resultado del CI en el PR.

### Más documentación

- Endpoints y contratos: [Backend/documents/endpoints.md](Backend/documents/endpoints.md)
- Errores, límites y seguridad: [Backend/documents/errores-y-seguridad.md](Backend/documents/errores-y-seguridad.md)
- Colección de Postman: [Backend/postman/README.md](Backend/postman/README.md)
- Índice completo: [Backend/documents/README.md](Backend/documents/README.md)

---

## Datos (analistas de datos)

Los datasets del equipo de datos van en **`Backend/data/`**.

- **Formatos**: CSV, JSON, GeoJSON o XLSX.
- **Nombres**: descriptivos, en minúsculas y sin espacios, por ejemplo `habilitaciones_comerciales_2025.csv`.
- **Fuente**: por cada dataset, agregar un `.md` con el mismo nombre (`habilitaciones_comerciales_2025.md`) que indique de dónde sale (URL), la fecha de descarga y qué significa cada columna.
- **Tamaño**: GitHub rechaza archivos de más de 100 MB y avisa desde los 50 MB. Si un archivo es más grande, dejar en el `.md` el link de descarga en lugar del archivo.
- **No subir** datos personales ni credenciales: solo datos públicos o anonimizados.
- Subirlos en una rama propia (`data/<nombre>`) y abrir un PR, como el resto del equipo.

La API no lee esta carpeta automáticamente: una vez subido un dataset, el equipo de backend lo integra al catálogo. Los datos que la API ya usa están en `Backend/app/db/*_snapshot.json`; ver [Backend/documents/snapshots-y-seed.md](Backend/documents/snapshots-y-seed.md).

---

## Frontend

<!-- Sección a completar por el equipo Frontend. -->

_A completar por el equipo Frontend._

### Requisitos

### Cómo correrlo

### Conexión con la API

La API corre en `http://localhost:8000` (ver [Backend con Docker](#backend-con-docker)).

### Más documentación

- [Frontend/README.md](Frontend/README.md)
