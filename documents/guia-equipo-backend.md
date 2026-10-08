# Guía del backend TECBA: qué resolvemos, con qué tecnologías

Documento para el **subequipo backend** (3 personas).  
Une lo ya acordado en arquitectura y plan de implementación con el análisis de fuentes y la presentación del equipo.

**Enfoque de este archivo:** solo backend. El frontend y el diseño del mapa los hacen otras áreas; nosotros les entregamos datos claros y confiables.

---

## 1. Para quién es este documento

Si trabajás en el backend de TECBA y querés entender:

- qué problema resolvemos,
- qué herramientas usamos,
- qué fuentes oficiales integramos,
- cómo repartimos el trabajo entre tres personas,
- y en qué orden avanzar,

este es tu punto de partida. Los detalles técnicos profundos de cada fuente están en [fuentes-pruebas.md](fuentes-pruebas.md).

---

## 2. Modelo del producto

### El problema

Una persona quiere iniciar una actividad (por ejemplo, abrir una cafetería) en un lugar de la Ciudad de Buenos Aires.  
Hoy la información está **dispersa**: un sitio habla de trámites, otro de mapas, otro de normativa del lote. No siempre se sabe por dónde empezar.

### La solución

Una plataforma que recibe la consulta en lenguaje natural (“quiero abrir una cafetería en Av. Corrientes 2500”) y responde con:

1. **Dónde** está ese lugar (dirección oficial, coordenadas, comuna, barrio).
2. **Qué** se permite ahí (normativa / usos del lote, cuando esté integrado).
3. **Cómo** habilitarlo (pasos, requisitos, documentación, con enlace oficial).
4. Datos para que el **frontend** dibuje el mapa y muestre las fuentes.

### Para quién

Ciudadanía de CABA (caso piloto: **abrir una cafetería**).  
Más adelante se pueden sumar otras actividades (ropa, alimentos, etc.), pero el camino feliz del MVP gira alrededor de la cafetería.

### Qué aporta el backend

El backend es el “cerebro de datos” de la plataforma:

- recibe la consulta,
- ubica la dirección,
- consulta o lee información oficial ya integrada,
- arma una respuesta ordenada,
- y **nunca inventa** un trámite, una coordenada o un requisito sin respaldo.

### Regla de oro

> La **IA ayuda a entender y explicar**.  
> La **información oficial** (APIs, datasets, páginas de trámites curadas) es la fuente de verdad.

Si falta un dato, se dice con claridad (“información no disponible”) y se muestra el resto. No se completa con una suposición del modelo.

### Cómo se “sostiene” el producto (visión de negocio)

No es un negocio de venta al público en el MVP. Es un **servicio de orientación ciudadana** basado en:

- datos públicos del Gobierno de la Ciudad,
- una capa de interpretación con IA,
- trazabilidad (cada bloque dice de dónde salió y cuándo).

El valor está en **ahorrar tiempo y reducir confusión**, no en reemplazar al organismo oficial ni en hacer el trámite por la persona.

---

## 3. Tecnologías que usamos

| Herramienta | Para qué sirve | En palabras simples |
|---|---|---|
| **Python** | Lenguaje del backend | El idioma en el que escribimos el servidor |
| **FastAPI** | Framework de la API | La herramienta que expone las “puertas” que el frontend llama |
| **PostgreSQL** | Base de datos | Donde guardamos actividades, trámites, fuentes, etc. |
| **PostGIS** | Extensión geográfica de PostgreSQL | Permite guardar y consultar puntos en el mapa |
| **Alembic** | Migraciones de base | Controla los cambios de tablas sin romper lo anterior |
| **Docker** | Contenedores | Levanta la base de datos (y opcionalmente la API) de forma repetible |
| **USIG** | Geocodificación oficial CABA | Convierte “Corrientes 2500” en coordenadas + barrio/comuna |
| **Ciudad 3D / epok** | Normativa del lote | Dice qué rubros / usos se permiten en ese lugar |
| **BA Data** | Catálogo de datos abiertos | Inventario de datasets para enriquecer contexto |
| **Trámites GCBA (HTML curado)** | Guía paso a paso | Pasos y requisitos oficiales (no hay API pública) |
| **LLM (IA)** | Interpretar y explicar | Lee la consulta y redacta la orientación **solo** con datos ya recuperados |
| **Postman** | Probar la API | Colección de pedidos para verificar cada endpoint |
| **httpx** | Cliente HTTP | Llama a USIG, epok y otros servicios desde el backend |

Variables de entorno típicas: `DATABASE_URL`, `LLM_*`, `GEOCODER_*` (ver `.env.example`).

---

## 4. Las fuentes oficiales y cómo se combinan

El MVP usa **tres fuentes principales** (más BA Data como apoyo de contexto). IDECABA queda como **cuarta fuente / futuro** (más capas de mapa).

| Fuente | Pregunta que responde | Estado |
|---|---|---|
| **USIG** | ¿Dónde es? | Funciona; ya integrado en el repo (Etapa 2) |
| **Ciudad 3D / epok** | ¿Qué se permite en ese lote? | API funciona; falta resolver bien el `smp` del lote |
| **Trámites GCBA** | ¿Cómo lo habilito? | Sin API; se cura / scrapea HTML con enlace oficial |
| **BA Data** | ¿Qué contexto hay? | Catálogo útil; cuidado con bloqueos (User-Agent) |
| **IDECABA** | Más capas de mapa | Futuro / ampliación |

### Flujo de combinación

```text
"Quiero abrir una cafetería en Av. Corrientes 2500"
        │
        ▼
   USIG  →  dirección oficial + lat/lng + comuna/barrio
        │
        ▼
  Ciudad 3D / epok  →  mixtura, rubros, usos del lote
        │
        ▼
  Trámites (+ BA Data)  →  pasos, requisitos, documentación, contexto
        │
        ▼
  Respuesta integrada  →  orientación + coords + fuentes citadas
```

**Ejemplo Corrientes 2500:** USIG ubica Balvanera / Comuna 3 → Ciudad 3D indica usos comerciales posibles → Trámites arma la guía (cuenta miBA, autorización, etc.) → cada bloque lleva su fuente.

**Claves que unen los datos:** coordenadas (lat/lng), a veces `smp` (sección-manzana-parcela), comuna/barrio, y el rubro de la actividad ligado al trámite correcto.

---

## 5. Qué ya está hecho vs qué falta

### Ya hecho en este repo (Etapas 0–2)

- Proyecto FastAPI con healthcheck.
- Base PostgreSQL/PostGIS con Docker.
- Catálogo seed (actividades, fuentes, oficinas, requisitos de ejemplo).
- Geocodificación USIG (y mock para pruebas): filtra CABA y completa comuna/barrio.
- Colección Postman inicial (Health, Catalog, Location).

### Falta (próximo foco backend)

- Consulta completa **sin IA** (camino feliz determinístico).
- Integrar **Ciudad 3D / epok** (parcela / `smp` / rubros).
- Reemplazar seeds de trámites por **guía curada** con URL oficial.
- ETL / carga desde **BA Data** (con las reglas del WAF).
- IA de interpretación y explicación.
- Preguntas de seguimiento y endurecimiento (trazabilidad, tests).

El plan operativo detallado por etapas sigue en [plan-implementacion.md](plan-implementacion.md). Esta guía lo resume y lo reparte entre tres roles.

---

## 6. Plan por etapas (backend)

Trabajo en paralelo entre A, B y C. Al cerrar cada etapa: **actualizar Postman** y probar juntos el camino feliz.

| Etapa | Objetivo en una frase | Estado |
|---|---|---|
| **0** | La API arranca y responde “estoy viva” | Hecha |
| **1** | Hay catálogo y datos mínimos en base | Hecha |
| **2** | Una dirección se convierte en punto + comuna/barrio | Hecha |
| **3** | Consulta completa **sin IA** (actividad + dirección → orientación) | Hecha |
| **3b** | Fuentes reales: epok + trámites curados (+ BA Data básico) | Hecha |
| **4** | La IA entiende la consulta en texto libre | Hecha |
| **5** | La IA explica solo con datos recuperados | Pendiente |
| **6** | Seguimiento, trazabilidad fuerte y pruebas | Pendiente |

### Etapa 3 — Consulta determinística

Armar `POST /api/v1/consultations` con actividad + dirección (sin chat todavía).  
Devuelve requisitos, pasos, oficinas, fuentes y coordenadas según [arquitectura-ia.md](arquitectura-ia.md).

### Etapa 3b — Fuentes reales (lo que suman fuentes-pruebas.md / presentación)

- Persona B: obtener `smp` real y conectar epok (rubros / mixtura).
- Persona C: cargar guía de trámites de cafetería con `url_fuente` + fecha.
- Persona A: orquestar la respuesta unificada y estados parciales si una fuente falla.

### Etapas 4–6 — IA y cierre

Interpretación → explicación respaldada → follow-ups → tests y despliegue.  
La IA **no** reemplaza a epok ni a los trámites curados.

---

## 7. Reparto entre tres personas

```text
Persona A (API e IA)  ──┐
Persona B (Ubicación y normativa) ──┼──▶  Consulta unificada al frontend
Persona C (Trámites y datos) ──┘
```

### Roles estables

| Rol | Responsabilidad principal | Ejemplos de archivos / temas |
|---|---|---|
| **Persona A — API e IA** | Endpoints de consulta, orquestación del flujo, Postman, prompts y validación de que la IA no invente | `app/api/`, `app/services/` (consultations, interpret, explain), `postman/` |
| **Persona B — Ubicación y normativa** | USIG, PostGIS, Ciudad 3D/epok, datos para el mapa (GeoJSON) | `app/providers/geocoder.py`, cliente epok, capas territoriales |
| **Persona C — Trámites y datos** | Catálogo, seeds, guía de trámites con URL oficial, ETL BA Data, metadatos de fuentes | `app/db/seed.py`, modelos de trámites/fuentes, scripts de carga |

### Dependencia con Análisis de Datos (fuera de este trio)

Ellos pueden entregar planillas curadas (trámites, equivalencias rubro → trámite, casos de prueba).  
El backend las **versiona, carga y automatiza**. No esperamos que Datos programe la API.

### Quién hace qué en cada etapa

#### Etapas 0–2 (ya hechas — referencia)

- **A:** estructura API, health, Postman base.
- **B:** geocoder USIG + filtro CABA + comuna/barrio.
- **C:** modelos, migraciones, seeds de catálogo.

#### Etapa 3 — Consulta sin IA

- **A:** endpoint `/consultations`, armar respuesta unificada, casos Postman.
- **B:** asegurar geocode estable para el flujo; preparar salida de ubicación lista para mapa.
- **C:** requisitos/oficinas/fuentes filtrables por actividad (seed mejorado si hace falta).

#### Etapa 3b — epok + trámites reales

- **A:** estados parciales (“epok no disponible”) y `source_ids` en cada bloque.
- **B:** cliente epok, resolución de `smp`, rubros/mixtura para cafetería.
- **C:** curaduría de trámites (pasos, docs, `url_fuente`, fecha) + primeras cargas BA Data.

#### Etapa 4 — Interpretación con IA

- **A:** cliente LLM, `/interpretations`, validar JSON y catálogo.
- **B:** apoyar si la IA pide aclarar ubicación ambigua.
- **C:** mantener catálogo de actividades alineado a lo que la IA puede elegir.

#### Etapa 5 — Explicación con IA

- **A:** explicación solo con contexto recuperado; rechazar claims sin fuente.
- **B:** aportar bloques territoriales correctos al contexto.
- **C:** aportar bloques de trámites/documentos correctos al contexto.

#### Etapa 6 — Seguimiento y cierre

- **A:** follow-ups, Postman e2e, manejo de errores de IA.
- **B:** robustez USIG/epok (timeouts, reintentos).
- **C:** trazabilidad completa y actualización periódica de trámites/datasets.

### Rituales del trio

1. Acordar el **contrato JSON** antes de programar cada etapa.
2. Cada PR/feature con endpoint nuevo **actualiza Postman**.
3. Integración corta semanal: probar juntos “cafetería en Corrientes 2500”.
4. Si una fuente cae: respuesta parcial + aviso, nunca inventar.

---

## 8. Reglas de oro del equipo

1. Solo CABA en el MVP (filtrar homónimos del Gran Buenos Aires).
2. Toda información “oficial” lleva **nombre de fuente + URL + fecha**.
3. La IA no inventa requisitos, oficinas ni coordenadas.
4. Si una fuente falla, se degrada con mensaje claro.
5. En BA Data: enviar `User-Agent` real; no depender de `package_search` (está bloqueado).
6. En epok: respetar rutas con barra final donde corresponda (ej. `/cur3d/categorias/`).
7. Trámites: no publicar pasos sin `url_fuente`.
8. Probar con Postman antes de dar por cerrada una etapa.

---

## 9. Qué entregamos al frontend (resumen)

| Servicio | Qué recibe el frontend |
|---|---|
| Consulta | Actividad + ubicación + orientación |
| Territorio | Comuna, barrio, datos de zona |
| Trámites | Pasos, requisitos, documentación + enlaces |
| Mapa | Coordenadas (+ capas cuando existan) |
| Fuentes | Origen de cada bloque |
| Chat / follow-up (más adelante) | Respuestas citadas dentro del mismo caso |

El formato detallado está en [arquitectura-ia.md](arquitectura-ia.md) (contrato de respuesta). La presentación del equipo muestra un JSON reducido solo a modo de ejemplo.

---

## 10. Glosario rápido

| Término | Significado simple |
|---|---|
| **API** | Conjunto de “puertas” por las que otra app pide o envía datos |
| **Endpoint** | Una puerta concreta (ej. `/health`, `/locations/geocode`) |
| **Backend** | La parte del sistema que procesa y guarda datos (este repo) |
| **Frontend** | La parte visual que usa la persona (otra área) |
| **Geocodificar** | Pasar de texto de dirección a coordenadas en el mapa |
| **PostGIS** | PostgreSQL con superpoderes geográficos |
| **Seed** | Datos de ejemplo cargados a mano para poder probar |
| **ETL** | Extraer, transformar y cargar datos desde una fuente hacia nuestra base |
| **smp** | Código de parcela (sección-manzana-parcela) usado por Ciudad 3D |
| **MVP** | Primera versión útil y demostrable, no el producto final completo |
| **Trazabilidad** | Poder decir de dónde salió cada dato y cuándo |
| **LLM / IA** | Modelo de lenguaje que interpreta o redacta texto |
| **Postman** | Herramienta para probar endpoints sin frontend |
| **WAF** | Filtro de seguridad del portal (puede bloquear pedidos “raros”) |

---

## 11. Comparación breve: ¿concuerda todo?

| Tema | ¿Alineado? | Comentario |
|---|---|---|
| Caso piloto cafetería / Corrientes 2500 | Sí | Mismo norte |
| IA no inventa | Sí | Regla compartida |
| Stack FastAPI + PostGIS + USIG | Sí | Ya en marcha |
| Tres fuentes MVP | Sí | Ahora concretadas: USIG + epok + Trámites |
| BA Data / IDECABA | Sí, con matices | BA Data como apoyo; IDECABA después |
| Etapas 0–2 del repo | Sí | Encajan con las pruebas de fuentes-pruebas.md |

**Aportes nuevos de fuentes-pruebas.md y presentacion.html** (ya incorporados en esta guía): fuentes concretas, claves de unión, reglas de USIG/epok/BA Data, y la necesidad de curar trámites sin API.

---

## 12. Referencias

| Documento | Para qué abrirlo |
|---|---|
| [fuentes-pruebas.md](fuentes-pruebas.md) | Pruebas reales de acceso a cada fuente |
| [../presentacion.html](../presentacion.html) | Presentación al equipo completo (si está en la raíz) |
| [arquitectura-ia.md](arquitectura-ia.md) | Flujo, contratos JSON, rol de la IA |
| [../PLAN.md](../PLAN.md) | Plan general del proyecto (todos los equipos) |
| [plan-implementacion.md](plan-implementacion.md) | Plan técnico por etapas de este repo |
| [`.cursor/agent/PLAN-EJECUCION.md`](../.cursor/agent/PLAN-EJECUCION.md) | Checklist de avance del agente / implementación |
| [README.md](README.md) | Índice de documentación |
| [../README.md](../README.md) | Cómo levantar el proyecto en local |
| [../postman/README.md](../postman/README.md) | Orden de pruebas en Postman |

---

*Última actualización: 2026-09-22. Solo backend. Caso piloto: cafetería en CABA.*
