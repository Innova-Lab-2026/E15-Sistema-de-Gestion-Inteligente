# Cómo actualizar `data/`

Guía para el equipo de Data: qué archivos lee el backend, con qué formato y cómo comprobar un cambio antes de subirlo.

## Archivos que lee el backend

| Archivo | Para qué lo usa el backend | Columnas |
|---|---|---|
| `barrios.csv` | Reconocer el barrio en la consulta ("peluquería en Belgrano"), pasar de barrio a comuna y buscar la sede comunal | `barrio_id,nombre,comuna,variantes` |
| `sinonimos.csv` | Pasar de las palabras de la persona a un rubro (`cafetería` → `rubro_102`). Manda sobre los sinónimos que tiene el código | `termino,rubro_code` |
| `consultas_prueba.csv` | Test automático: cada fila es un caso que el intérprete sin IA tiene que resolver | `pregunta,rubro_esperado,barrio_esperado` y, opcional, `estado_esperado` |
| `<archivo>.meta.json` | Fuente que se muestra en la respuesta: nombre, URL, organismo, licencia y fechas | `nombre, url, organismo, licencia, publicado, descargado` |

Un `.csv` con otro nombre (por ejemplo `consultas_prueba (1).csv`) no lo lee nadie: el test de formato avisa.

## Reglas de formato

- UTF-8 **sin BOM**, separador coma, primera fila con los nombres de columna exactos.
- `barrios.csv`
  - `barrio_id` en minúsculas, sin tildes, con `_` (`villa_general_mitre`), sin repetir. Tienen que estar los 48 barrios.
  - `comuna` es un número del 1 al 15.
  - `variantes` separadas por `|`. Mayúsculas, tildes y puntos no importan ("VILLA GRAL. MITRE" = "villa gral mitre"). Una variante no puede servir para dos barrios.
  - Las variantes con errores de codificación a propósito (`NÃºÃ±ez`) están bien; una codificada dos veces (`NuÃƒÂ±ez`) no.
- `sinonimos.csv`
  - `rubro_code` tiene que existir en el catálogo de Ciudad 3D (`app/db/epok_rubros_snapshot.json`).
  - Un término no se repite. "cafeteria" y "cafetería" pueden estar los dos, pero con el mismo rubro.
  - El backend busca palabras completas y acepta plurales: "kiosco" también encuentra "kioscos".
- `consultas_prueba.csv`
  - `rubro_esperado` vacío si la consulta no tiene rubro; `barrio_esperado` es un `barrio_id` o vacío.
  - `estado_esperado`: `completa`, `pide_aclaracion` o `fuera_de_alcance`.
- `.meta.json`: las fechas `publicado` y `descargado` en formato `AAAA-MM-DD`.

## Comprobar un cambio

Con la base levantada (`make up`):

```bash
make tests ARGS="-k data_"
```

- `test_data_files.py` revisa el formato y dice archivo, fila y qué arreglar.
- `test_data_queries.py` corre cada fila de `consultas_prueba.csv`. Una consulta nueva se suma sola como caso.

Mientras falten `sinonimos.meta.json` y `consultas_prueba.meta.json`, el test los marca como `xfail` (pendientes). Cuando lleguen, sacarlos de `META_PENDIENTES` en `tests/test_data_files.py`.

## Después de cambiar un archivo

- Tests y desarrollo local leen `data/` directo.
- La imagen de Docker copia `data/` al construirse: `make build` (o `make up`) para que la API use el archivo nuevo.
- Las fuentes de los `.meta.json` se cargan en la base con el seed (`make migrate`).

## Lo que el sistema no entendió

Cada vez que una persona nombra una actividad que no está en el catálogo, el backend guarda las palabras que usó (no la consulta completa) y, si después elige un rubro, cuál. Para armar la lista de sinónimos nuevos:

```bash
python -m scripts.export_unrecognized --since 2026-11-01
```

Genera `actividades_no_reconocidas.csv` con `termino`, `rubro_code` (el más elegido), `veces`, `veces_elegido`, `candidatos` y fechas. Las columnas `termino` y `rubro_code` son las mismas de `sinonimos.csv`.

## Decisiones pendientes con Data

En `app/db/catalog_data.py`, `PENDING_SYNONYMS` mantiene el comportamiento anterior para tres términos hasta que Data confirme el rubro: `veterinaria` (¿136 o 104?), `confitería` (¿102 o 471?) y `comercio minorista` (¿se saca?). Los sinónimos del código para rubros que el CSV no tiene (`CITIZEN_ALIASES`) se usan solo para términos que el CSV no define.
