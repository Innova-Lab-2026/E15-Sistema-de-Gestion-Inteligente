# Fuentes de información – Pruebas rápidas de acceso (MVP TECBA)

Fecha: 2026-09-22
Caso piloto: **“Quiero abrir una cafetería en Av. Corrientes 2500. ¿Qué tengo que hacer?”**
Método: `curl` + verificación de endpoints públicos. Sin API keys.

> Conclusión: las 4 fuentes son utilizables para el MVP, con matices.
> Stack de 3 fuentes recomendado: **USIG + Ciudad 3D/epok + Trámites curados + datasets BA Data descargados**.

---

## 0. Resumen ejecutivo – qué hace cada fuente y por qué la usamos

| Fuente | Qué es / qué hace | Por qué la usamos en el MVP | Qué queremos sacar |
|---|---|---|---|
| **USIG** (geocodificación + datos útiles) | API oficial de la Ciudad que normaliza direcciones (`"Corrientes 2500"` → dirección oficial + `lat/lng`) y devuelve contexto territorial del punto (comuna, barrio, comisaría, hospital, escuela, sección catastral). | Es la **puerta de entrada**: sin coordenadas no hay mapa, ni parcela, ni mixtura, ni trámites territorializados. Resuelve el “¿dónde?” de la consulta en lenguaje natural. | `direccion_normalizada, lat, lng (SRID 4326), comuna, barrio, seccion_catastral, comisaria, area_hospitalaria, distrito_escolar` |
| **Ciudad 3D / epok** (normativa + catastro) | API del Código Urbanístico: dado un punto o `smp` (sección-manzana-parcela) devuelve qué **se puede construir y qué rubros están permitidos** (categorías, mixturas, rubros, edificabilidad, afectaciones, obras). | Responde el “¿qué puedo hacer acá?”. Es la única fuente que cruza **actividad × ubicación** a nivel normativo (ej: cafetería en Mixtura 2). | `smp, mixtura, categorias[10], rubros[{rubro, rubro_id}], usos_permitidos, edificabilidad, afectaciones, geometria, fotos_fachada` |
| **BA Data (CKAN)** (catálogo abierto) | Catálogo de 454 datasets tabulares/geográficos (CSV, XLSX, JSON, GeoJSON, APIs documentadas). Es el **inventario** de qué datos existen y dónde descargarlos. | Nos da **volumen y contexto** (ej: locales gastronómicos, datos útiles, catastro) para enriquecer la respuesta y poblar PostGIS vía ETL. Varios datasets simplemente documentan las APIs de USIG/epok. | `package_list → package_show → resources[].url → ETL → PostGIS`; `titulo, organizacion, licencia, fecha, formato, url_descarga` |
| **Trámites (buenosaires.gob.ar)** (guía oficial) | Páginas oficiales con **pasos, requisitos, documentación y tipos de habilitación** (común, exprés <200 m², DDRR, licencia). No tiene API: se lee como HTML. | Construye el **camino feliz** (“qué tengo que hacer, en qué orden, con qué papeles”). Sin esto solo mostramos datos, no orientación accionable. | `tramite{titulo, tipo, superficie_max, requiere_profesional}, pasos[ordenados], requisitos[], documentacion[], url_fuente, fecha_scrapeo` |
| **IDECABA** (geoportal – 4ª fuente / futuro) | Geoportal con visor + catálogo Geonetwork + servicios OGC (WMS/WFS/tiles). Es la **capas geográficas finas** de la Ciudad. | En el MVP la usamos como **ampliación** (más capas para el mapa). El núcleo territorial ya lo cubren USIG + epok. | `capas[{nombre, endpoint WMS/WFS, campos, bbox}]` (a relevar en Sprint 1 con DevTools) |

### Cómo se complementan entre sí

```
"Quiero abrir una cafetería en Av. Corrientes 2500"
        │
        ▼
┌──────────────┐  direccion_normalizada + lat/lng   ┌──────────────────┐
│     USIG     │ ─────────────────────────────────▶ │ Ciudad 3D / epok │
│  ¿DÓNDE es?  │  (-58.401981, -34.604792) +        │ ¿QUÉ se permite? │
│ comuna 3,    │   seccion_catastral 09 → smp       │ mixtura, rubros, │
│ Balvanera    │                                    │ edificabilidad   │
└──────┬───────┘                                    └────────┬─────────┘
       │ comuna/barrio/smp                                   │ rubro cafetería + mixtura
       ▼                                                     ▼
┌──────────────┐  datasets de contexto  ┌─────────────────────────────────┐
│   BA Data    │ ─────────────────────▶ │     Trámites (guía oficial)     │
│ ¿QUÉ contexto│  (gastronómicos,       │ ¿CÓMO lo habilito?              │
│ hay?         │   catastro, servicios) │ pasos + requisitos + docs       │
└──────────────┘                        └────────────────┬────────────────┘
                                                         ▼
                                              ┌─────────────────────┐
                                              │ Respuesta integrada │
                                              │ mapa + pasos +      │
                                              │ territorio + fuentes│
                                              └─────────────────────┘
```

- **Claves de unión:** `lat/lng (4326)` → USIG ↔ epok ↔ PostGIS; `smp` → epok ↔ catastro ↔ fotos; `comuna/barrio/sección` → USIG ↔ datasets BA Data; `rubro/categoría` → epok ↔ trámites (qué habilitación corresponde a cafetería); `url_fuente + fecha` → todas ↔ trazabilidad.
- **Ejemplo Corrientes 2500:** USIG dice *Balvanera, Comuna 3, -58.40/-34.60* → epok dice *categoría Comercial, rubros de alimentación permitidos en Mixtura 2* → BA Data aporta *contexto (locales, servicios)* → Trámites arma *guía: miBA → Ciudad 3D → AGC + CAA → autoprotección (exprés si <200 m²)*.
- **Si una fuente cae:** la respuesta sigue siendo parcial pero útil (USIG es crítica; epok/trámites degradan a mensaje “info no disponible” con fuente citada, nunca inventada).

---

## 1. USIG – Geocodificación y datos territoriales ✅

**Estado: FUNCIONA. Sin key. Prioridad: base obligatoria.**

Convierte dirección en lenguaje natural → coordenadas + contexto territorial. Es el punto de entrada de todo el flujo `qué + dónde`.

### Endpoints verificados

| Endpoint | Resultado |
|---|---|
| `GET https://servicios.usig.buenosaires.gob.ar/normalizar/?direccion=Corrientes 2500&maxOptions=3&geocodificar=TRUE` | `200` – coords + dirección normalizada |
| `GET https://ws.usig.buenosaires.gob.ar/datos_utiles?x=-58.401981&y=-34.604792` | `200` – comuna, barrio, comisaría, hospital, distrito escolar |
| `GET https://mapa.buenosaires.gob.ar/` | `200` – visor alternativo |

### Ejemplo real (Corrientes 2500)

```json
// normalizar/
{
  "altura": 2500,
  "direccion": "CORRIENTES AV. 2500, CABA",
  "nombre_calle": "CORRIENTES AV.",
  "coordenadas": { "srid": 4326, "x": "-58.401981", "y": "-34.604792" },
  "tipo": "calle_altura"
}
```

```json
// datos_utiles?x=-58.401981&y=-34.604792
{
  "comuna": "Comuna 3",
  "barrio": "Balvanera",
  "comisaria": "7",
  "area_hospitalaria": "HTAL. DR. J.M. RAMOS MEJÍA",
  "region_sanitaria": "I (Este)",
  "distrito_escolar": "Distrito Escolar I",
  "seccion_catastral": "09"
}
```

### Notas backend
- Filtrar por `cod_partido == "caba"` / `nombre_partido == "CABA"`: la búsqueda también devuelve Moreno, Quilmes, San Isidro, etc.
- SRID `4326` directo a PostGIS (`ST_SetSRID(ST_MakePoint(x, y), 4326)`).
- Documentación oficial del dataset en BA Data: `api-geocodificador-direcciones-caba`, `api-consulta-datos-utiles` → `https://usig.buenosaires.gob.ar/apis/`.

---

## 2. BA Data (CKAN) ⚠️ – Catálogo de datos abiertos

**Estado: PARCIAL. Sin key. Requiere `User-Agent` y workaround por WAF.**

Portal: `https://data.buenosaires.gob.ar` – CKAN `2.11.0`, **454 datasets** (contados vía `package_list`).

### Endpoints verificados

| Endpoint | Resultado |
|---|---|
| `GET /api/3/action/status_show` | `200` ✅ (con `User-Agent`) |
| `GET /api/3/action/package_list` | `200` ✅ – 454 ids |
| `GET /api/3/action/package_show?id=<id>` | `200` ✅ (por GET; por POST lo bloquea el WAF) |
| `GET /api/3/action/organization_list` | `200` ✅ |
| `GET /api/3/action/group_list` | `200` ✅ (8 grupos) |
| `GET /api/3/action/tag_list` | `200` ✅ |
| `GET /api/3/action/current_package_list_with_resources?limit=2` | `200` ✅ |
| `GET/POST /api/3/action/package_search` | ❌ `Request Rejected` (WAF, con y sin `q`, GET y POST) |
| `.../datastore_search`, `.../resource_search` | ❌ `Request Rejected` (WAF) |
| `GET portal /` y `datosabiertos-apis.buenosaires.gob.ar/...?schema_name=ba_data` | `200` ✅ |

> Sin header `User-Agent: Mozilla/5.0` hasta `status_show` devuelve `Request Rejected`. **El backend debe enviar siempre `User-Agent` + timeout + reintentos.**

### Ejemplos reales

```bash
curl -A "Mozilla/5.0" "https://data.buenosaires.gob.ar/api/3/action/package_show?id=api-consulta-datos-catastrales-caba"
# → title: "API Consulta de Datos Catastrales de CABA"
#   resource: Catastro | API | https://epok.buenosaires.gob.ar/catastro/datos-catastrales.png

curl -A "Mozilla/5.0" "https://data.buenosaires.gob.ar/api/3/action/package_show?id=api-consulta-datos-utiles"
# → title: "API Consulta de datos útiles"
#   url: https://usig.buenosaires.gob.ar/apis/
```

Ids útiles vistos en `package_list`: `api-consulta-datos-catastrales-caba`, `api-consulta-datos-utiles`, `api-geocodificador-direcciones-caba`, `api-busqueda-lugares-interes`.

### Notas backend
- `package_search` bloqueado → **no usar búsqueda full-text del CKAN**. Estrategia: `package_list` → `package_show?id=` por cada id → filtrar en Python por título/tags → descargar `resources[].url` (CSV/XLSX/JSON/GeoJSON) al ETL → cargar a PostGIS.
- Muchos datasets “API/GTFS/Transporte” figuran como suspendidos en el portal: validar recurso por recurso.
- Guardar `metadata_created`, `license_id` (`CC-BY-2.5-AR` típico) para trazabilidad.

---

## 3. Ciudad 3D / epok ✅ – Normativa urbanística y catastro

**Estado: FUNCIONA. Sin key. Fuente diferencial para mixturas/rubros.**

- Visor: `https://ciudad3d.buenosaires.gob.ar/` (`200`, SPA Vite + `config.js`).
- API real: `https://epok.buenosaires.gob.ar` (rutas extraídas de `gcba/Ciudad-3D/source/src/utils/apiConfig.js`).
- Repos: `gcba/Ciudad-3D`, `datosgcba/Ciudad-3D` (frontend React+Redux, backend Django + Postgres+PostGIS, vector tiles Mapbox GL).
- `config.js` verificado: `urlAPI: https://epok.buenosaires.gob.ar`, `urlVectorTile: https://vectortiles.usig.buenosaires.gob.ar/cur3d/`, `urlWsUsig`, `urlPhoto: https://fotos.usig.buenosaires.gob.ar`, etc.

### Endpoints verificados

| Endpoint | Resultado |
|---|---|
| `GET /cur3d/categorias/` | `200` ✅ – 10 categorías (**con trailing slash; sin slash devuelve vacío**) |
| `GET /cur3d/cuadrosdeuso/rubros/?categoria=1&mixtura=2` | `200` ✅ – rubros comerciales/gastronómicos |
| `GET /catastro/parcela/?lng=-58.401981&lat=-34.604792` | `200` pero `{}` – pendiente resolver `smp` real |
| `GET /catastro/parcela/?smp=023-012-003` | `200` pero `{}` – formato `smp` de prueba no válido |
| `GET https://fotos.usig.buenosaires.gob.ar/getDatosFotos?smp=023-012-003` | `200` `([])` |
| `GET /cur3d/...` resto (`mixtura_usos/?smp=`, `afectaciones/?smp=`, `edificabilidad/?smp=`, `obras/?smp=`, `geometria/?smp=`) | Definidos en `apiConfig.js`, pendientes de probar con `smp` real (Sprint 1) |
| `GET https://vectortiles.usig.buenosaires.gob.ar/cur3d/` (raíz) | `404` (esperable; se usa con path de tile completo) |

### Ejemplos reales

```json
// GET /cur3d/categorias/
[{"id":1,"nombre":"Comercial"},{"id":2,"nombre":"Depositos, Almacenamiento y logística"},
 {"id":3,"nombre":"Servicios"},{"id":4,"nombre":"Alojamiento"},{"id":5,"nombre":"Transporte"},
 {"id":6,"nombre":"Diversiones publicas, cultura, culto y recreacion"},{"id":7,"nombre":"Educacion"},
 {"id":8,"nombre":"Sanidad"},{"id":9,"nombre":"Residencial"},{"id":10,"nombre":"Industria"}]
```

```json
// GET /cur3d/cuadrosdeuso/rubros/?categoria=1&mixtura=2 (recorte)
{"rubros":[
  {"rubro":"1.6. Comercio minorista alimenticios por sistema de venta","rubro_id":11},
  {"rubro":"1.5.3 Alimentación en general para llevar","rubro_id":471},
  {"rubro":"1.4. Comercio minorista de productos de abasto y alimenticios","rubro_id":103},
  {"rubro":"1.4.3. Maxikiosco","rubro_id":169}]}
```

### Notas backend
- Siempre usar trailing slash en `/cur3d/categorias/`.
- El `smp` (sección-manzana-parcela) es la llave de casi todo (`mixtura_usos`, `afectaciones`, `edificabilidad`, `obras`, `sade`, `inspecciones`, `plusvalía`). Sprint 1: obtener `smp` real de Corrientes 2500 vía `catastro/parcela/?lng=&lat=` (probar orden de coords / precisión) o vía USIG, y luego encadenar `mixtura_usos → rubros → referencias`.
- Fotos de fachada: `fotos.usig.../getDatosFotos?smp=` + `getFoto?smp=&i=&w=`.

---

## 4. Trámites (buenosaires.gob.ar) ❌ Sin API – HTML scrapeable

**Estado: SIN API PÚBLICA. HTML accesible para scraping + curaduría manual.**

| URL | Resultado |
|---|---|
| `/tramites/habilitacion-de-actividad-economica` | `200` (~69 KB), `<h1>Habilitación de actividad económica</h1>` |
| `/tramites/habilitacion-de-actividad-economica-expres` | `200` (requisitos <200 m², sin evaluación técnica) |
| `/tramites/como-habilitar-tu-local-comercial-en-la-ciudad` | `200` – guía paso a paso 1-6 (miBA → apoderamientos → Ciudad 3D → consulta de usos → autorización AGC + CAA → autoprotección) |
| `/tramites` | `301` → home (existe, con redirect) |
| Plataforma TAD/SSIT (AGC) | Requiere login miBA nivel 2/3 – **no automatizable** |

### Contenido aprovechable para el camino feliz (cafetería)
1. Crear cuenta miBA → 2. Apoderamientos (Clave Ciudad AGIP/TAD) → 3. Revisar normativa del lote en Ciudad 3D + Código Urbanístico Ley 6099/2018 → 4. Consulta de usos / visados → 5. Autorización de Actividad Económica (común o exprés <200 m² + CAA automático) con Anexo Técnico de profesional matriculado → 6. Sistema de Autoprotección (Grupo 1 = DDJJ; 2/3 = aprobación). Tipos: DDRR sin plano (hasta 500 m², inicio inmediato + QR), DDRR con plano, Licencia (requiere inspección previa, validez 15 años).

### Notas backend
- Modelo sugerido: tablas `tramites(id, titulo, url_fuente, tipo, superficie_max, requiere_profesional, ...)`, `requisitos`, `pasos`, `documentacion`, con `fuente_url` + `fecha_scrapeo` para trazabilidad.
- Re-scrapeo periódico + diff; si cambia el HTML, marcar para revisión manual. No presentar como oficial nada sin `url_fuente`.

---

## 5. IDECABA ⚠️ – Geoportal (requiere Sprint 1)

**Estado: ACCESIBLE COMO SPA. APIs internas por confirmar con DevTools.**

- `https://idecaba.buenosaires.gob.ar/` → `200` (React SPA, `create-react-app`, `<div id="root">`).
- `env.js` verificado:
  - `REACT_APP_API_URL: https://admin-idecaba.buenosaires.gob.ar/` → `200`
  - `REACT_APP_GEONETWORK_URL: https://geonetwork-idecaba.buenosaires.gob.ar/geonetwork/` (catálogo CSW; `POST .../srv/api/search/records/_search` devolvió vacío con body de prueba – ajustar query)
  - `REACT_APP_PORTAL_URL: https://visualizador-idecaba.buenosaires.gob.ar/` → `200`
  - Login externo: `identidad-gcaba.../realms/open-id/...` (Keycloak)
- Pendiente Sprint 1: abrir el visualizador con DevTools → capturar WMS/WFS/VectorTiles/GeoJSON reales y documentar `layer → endpoint → campos`.

---

## 6. Decisión para el MVP (qué 3 fuentes integrar)

| # | Fuente | Rol en `actividad + territorio + trámites` | Riesgo |
|---|---|---|---|
| 1 | **USIG** | Geocodificación + contexto territorial (comuna/barrio/sección) | Bajo |
| 2 | **Ciudad 3D / epok** | Mixtura, usos permitidos, rubros, edificabilidad | Medio (resolver `smp`) |
| 3 | **Trámites curados + datasets BA Data** | Pasos, requisitos, documentación + capas tabulares en PostGIS | Medio (scraping + WAF) |

IDECABA queda como 4ª fuente / ampliación (capas WMS/WFS del visualizador).

## 7. Reglas transversales backend (de las pruebas)

1. **Siempre enviar `User-Agent` real** (BA Data bloquea curl por defecto).
2. **Trailing slash** en `epok /cur3d/categorias/`.
3. Filtrar USIG a `CABA` (hay homónimos en GBA).
4. Guardar en cada respuesta: `fuente_nombre, fuente_url, fecha_consulta/actualización` (trazabilidad exigida por el PDF).
5. ETL BA Data sin `package_search`: `package_list → package_show → download resources → PostGIS`.
6. Trámites: solo contenido con `url_fuente`; revalidación periódica.
