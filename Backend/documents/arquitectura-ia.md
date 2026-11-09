# Arquitectura de IA y Geolocalizacion — TECBA

## 1. Objetivo

Definir como la plataforma recibe una consulta ciudadana en lenguaje natural, identifica la actividad y la ubicacion, consulta informacion oficial contextualizada y devuelve una orientacion verificable junto con coordenadas para visualizarla en el frontend.

El alcance inicial es la **Ciudad Autonoma de Buenos Aires (CABA)**. En este contexto se utilizan comuna, barrio y organismo o jurisdiccion competente. No se asume una municipalidad externa.

## 2. Principio central

La IA es necesaria, pero no es la fuente de verdad.

La IA se utiliza para:

- Interpretar el lenguaje natural.
- Detectar la intencion de la persona.
- Extraer la actividad y la direccion.
- Proponer una categoria normalizada.
- Detectar ambiguedades y pedir aclaraciones.
- Organizar y explicar la informacion recuperada.

La informacion oficial proviene de:

- Catalogos y datasets previamente integrados.
- APIs oficiales.
- Documentos oficiales procesados y citables.
- Servicios de geocodificacion y datos geograficos validados.
- Reglas deterministicas del backend.

La IA nunca debe inventar requisitos, decidir por si sola la jurisdiccion, generar coordenadas sin validacion ni consultar la web abierta sin trazabilidad.

## 3. Flujo general

```text
Consulta en lenguaje natural
        |
        v
Interpretacion IA: intencion, actividad y direccion
        |
        v
Validacion del JSON y del catalogo de actividades
        |
        v
Geocodificacion de la direccion
        |
        v
Determinacion de comuna, barrio y organismo competente
        |
        v
Recuperacion de fuentes oficiales por actividad y ubicacion
        |
        v
Orientacion estructurada: requisitos, documentos y pasos
        |
        v
Busqueda de canales online y oficinas fisicas
        |
        v
Generacion de explicacion respaldada por fuentes
        |
        v
Respuesta al frontend con coordenadas y metadatos
```

## 4. Ejemplo de consulta

Consulta de entrada:

> Quiero abrir un local de ropa en Av. Corrientes 2500. Que tengo que hacer?

Interpretacion esperada:

- Intencion: iniciar una actividad comercial.
- Actividad original: local de ropa.
- Categoria normalizada: comercio de indumentaria.
- Direccion original: Av. Corrientes 2500.
- Jurisdiccion: CABA.
- Estado: requiere geocodificacion y confirmacion del usuario.

La interfaz debe mostrar la actividad y la direccion detectadas para que la persona pueda corregirlas antes de iniciar la consulta oficial.

## 5. Interpretacion de lenguaje natural

### 5.1 Entrada

El backend recibe texto libre en espanol y un identificador opcional de conversacion:

```json
{
  "query": "Quiero abrir un local de ropa en Av. Corrientes 2500. Que tengo que hacer?",
  "conversation_id": null,
  "confirmed_location": null
}
```

### 5.2 Salida estructurada de la IA

La IA debe devolver JSON validado contra un esquema. El backend no debe utilizar directamente una respuesta de texto libre para consultar fuentes.

```json
{
  "intent": "start_commercial_activity",
  "activity": {
    "raw_text": "local de ropa",
    "normalized_category": "rubro_16",
    "display_name": "Comercio de indumentaria",
    "confidence": 0.96
  },
  "location": {
    "raw_text": "Av. Corrientes 2500",
    "address": null,
    "confidence": 0.94
  },
  "jurisdiction": "CABA",
  "missing_fields": [],
  "clarification_question": null,
  "status": "ready_for_geocoding"
}
```

### 5.3 Casos que requieren aclaracion

La plataforma debe pedir aclaracion cuando:

- No se detecta una actividad.
- La actividad no pertenece al catalogo del MVP.
- La direccion es incompleta o ambigua.
- La direccion parece estar fuera de CABA.
- Existen varias coincidencias de geocodificacion.
- La consulta combina varias actividades que no pueden resolverse juntas.

Ejemplo:

> Detecte la actividad “local de ropa”, pero la direccion puede corresponder a dos ubicaciones. Selecciona la correcta en el mapa para continuar.

## 6. Catalogo de actividades

El MVP debe utilizar un catalogo controlado. La IA propone una categoria y el backend la valida.

Ejemplos iniciales:

| Codigo | Nombre | Ejemplo |
|---|---|---|
| `rubro_16` | 1.8. Comercio minorista excluido comestibles… | Local de ropa (alias) |
| `rubro_102` | 1.5. Alimentación en general y gastronomía | Abrir una cafeteria (alias) |
| `rubro_471` | 1.5.3 Alimentación en general para llevar | Confiteria / panaderia (alias) |

El catalogo debe poder ampliarse sin modificar el flujo general. Si la actividad no tiene una categoria habilitada, la respuesta debe indicar que esta fuera del alcance actual, sin inventar tramites.

## 7. Geocodificacion y jurisdiccion

### 7.1 Proceso

1. Recibir la direccion extraida.
2. Enviarla a un servicio de geocodificacion elegido para el proyecto.
3. Normalizar calle, altura, barrio y ciudad.
4. Devolver latitud, longitud, nivel de precision y posibles coincidencias.
5. Determinar comuna y barrio usando datos geograficos validados de CABA/PostGIS.
6. Solicitar confirmacion cuando la precision sea insuficiente o existan varias coincidencias.

### 7.2 Resultado de ubicacion

```json
{
  "status": "confirmed",
  "original_address": "Av. Corrientes 2500",
  "normalized_address": "Avenida Corrientes 2500, CABA",
  "city": "Ciudad Autonoma de Buenos Aires",
  "commune": "Comuna 5",
  "neighborhood": "Almagro",
  "latitude": -34.604,
  "longitude": -58.413,
  "precision": "rooftop",
  "source": {
    "id": "geocoder-caba",
    "name": "Servicio de geocodificacion utilizado",
    "retrieved_at": "2026-09-21T00:00:00Z"
  }
}
```

Las coordenadas devueltas por el geocodificador deben validarse antes de almacenarse o mostrarse. Las coordenadas de oficinas y lugares de tramite deben geocodificarse preferentemente durante la ingesta de datos, no en cada consulta.

## 8. Fuentes oficiales y recuperacion

El backend debe mantener un catalogo de fuentes con metadatos completos. Como minimo, el MVP debe integrar tres fuentes tecnicamente viables.

Cada registro debe conservar:

- Identificador de la fuente.
- Organismo responsable.
- URL o identificador oficial.
- Tipo de fuente.
- Jurisdiccion.
- Actividades relacionadas.
- Fecha de publicacion o actualizacion.
- Fecha de ingesta.
- Vigencia y estado de disponibilidad.
- Regla de transformacion aplicada.
- Enlace de respaldo para la persona usuaria.

Las fuentes pueden cubrir funciones diferentes:

1. **Tramites y requisitos:** condiciones, documentacion y pasos.
2. **Informacion territorial:** uso del suelo, restricciones, zonificacion y capas geograficas.
3. **Lugares de atencion:** oficinas, organismos, canales y puntos de tramite.

La recuperacion debe filtrar por:

- Categoria de actividad.
- Coordenadas de la ubicacion.
- CABA y comuna o area correspondiente.
- Organismo competente.
- Vigencia de la informacion.

La IA puede ayudar a explicar los resultados, pero la seleccion de los requisitos debe realizarla el backend utilizando registros y documentos previamente integrados.

## 9. Requisitos, documentacion y pasos

Cada requisito debe estar relacionado con una fuente concreta.

```json
{
  "id": "requirement-001",
  "title": "Habilitacion del establecimiento",
  "description": "Descripcion tomada de la informacion oficial integrada.",
  "documents": [
    {
      "name": "Documento requerido",
      "details": "Detalle disponible en la fuente oficial"
    }
  ],
  "steps": [
    {
      "order": 1,
      "title": "Iniciar el tramite",
      "description": "Paso respaldado por la fuente oficial"
    }
  ],
  "source_ids": ["source-001"],
  "status": "available"
}
```

Estados posibles:

- `available`: informacion disponible y vigente.
- `partial`: informacion incompleta.
- `outdated`: requiere verificacion por antiguedad.
- `not_available`: la fuente no esta disponible.
- `not_applicable`: no corresponde a la actividad o ubicacion.

## 10. Lugares de tramite y coordenadas

La respuesta debe incluir tramites online y oficinas fisicas cuando exista informacion oficial.

Cada lugar fisico debe devolver:

- Nombre.
- Organismo.
- Tipo de lugar.
- Direccion.
- Horario, si esta publicado.
- URL oficial.
- Latitud.
- Longitud.
- Distancia opcional desde la ubicacion consultada.
- Fuente y fecha de actualizacion.

```json
{
  "id": "office-001",
  "name": "Oficina de atencion",
  "organization": "Organismo oficial",
  "type": "physical_office",
  "address": "Direccion oficial del lugar",
  "opening_hours": null,
  "url": "https://sitio-oficial.example/tramite",
  "latitude": -34.603,
  "longitude": -58.412,
  "distance_meters": 250,
  "source_ids": ["source-003"],
  "status": "available"
}
```

El frontend debe distinguir visualmente:

- La ubicacion consultada.
- Oficinas o lugares de tramite.
- Capas territoriales.
- Puntos de interes adicionales.

## 11. Contrato de respuesta para el frontend

El endpoint principal puede ser `POST /api/v1/consultations`.

Respuesta de referencia:

```json
{
  "consultation_id": "consultation-001",
  "status": "complete",
  "interpretation": {
    "intent": "start_commercial_activity",
    "activity": {
      "normalized_category": "rubro_16",
      "display_name": "Comercio de indumentaria",
      "confidence": 0.96
    },
    "original_query": "Quiero abrir un local de ropa en Av. Corrientes 2500. Que tengo que hacer?"
  },
  "location": {
    "normalized_address": "Avenida Corrientes 2500, CABA",
    "commune": "Comuna 5",
    "neighborhood": "Almagro",
    "latitude": -34.604,
    "longitude": -58.413,
    "precision": "rooftop",
    "status": "confirmed"
  },
  "summary": "Orientacion generada a partir de la informacion oficial recuperada.",
  "requirements": [],
  "documents": [],
  "steps": [],
  "territorial_information": [],
  "online_procedures": [],
  "physical_offices": [],
  "map_layers": [],
  "sources": [],
  "data_status": {
    "overall": "complete",
    "missing": [],
    "warnings": []
  }
}
```

Todos los bloques de contenido deben incluir `source_ids`. La respuesta no debe incluir afirmaciones oficiales sin una fuente asociada.

## 12. Rol de la IA en la respuesta final

Se recomienda separar la IA en dos etapas:

### Etapa A: interpretacion

- Extraer intencion, actividad y direccion.
- Clasificar la actividad.
- Detectar datos faltantes.
- Devolver JSON validado.

### Etapa B: explicacion

- Recibir como contexto solo los resultados oficiales recuperados.
- Ordenar requisitos, documentacion y pasos.
- Redactar una explicacion clara para la ciudadania.
- Mantener las referencias de cada bloque.
- Indicar explicitamente cuando falta informacion.

El modelo no debe tener permiso logico para agregar datos fuera del contexto recibido. El backend debe validar el esquema y rechazar respuestas sin fuentes, con coordenadas invalidas o con requisitos no respaldados.

## 13. Experiencia del usuario

1. La persona escribe su necesidad en lenguaje natural.
2. El sistema muestra la actividad y la direccion detectadas.
3. La persona puede corregir la actividad o elegir una coincidencia de direccion.
4. El mapa muestra la ubicacion confirmada.
5. El sistema consulta fuentes oficiales.
6. La respuesta presenta resumen, requisitos, documentacion y pasos.
7. El mapa agrega capas territoriales y lugares de tramite.
8. Cada bloque muestra organismo, fuente y fecha de actualizacion.
9. La persona puede realizar preguntas de seguimiento dentro del caso confirmado.

## 14. Estados y errores

La interfaz y la API deben contemplar:

- Consulta valida.
- Actividad no reconocida.
- Actividad fuera del alcance.
- Direccion no reconocida.
- Direccion ambigua.
- Ubicacion fuera de CABA.
- Fuente temporalmente no disponible.
- Informacion parcial.
- Informacion desactualizada.
- Sin oficinas fisicas publicadas.
- Sin tramite online publicado.
- Error del proveedor de IA.
- Limite de solicitudes del proveedor.

En ningun caso se debe completar silenciosamente un dato faltante con una suposicion del modelo.

## 15. Stack sugerido

- Frontend: React o Next.js.
- Backend: Python y FastAPI.
- Base de datos: PostgreSQL con PostGIS.
- Procesamiento: Python, Pandas y GeoPandas.
- Formatos: JSON, CSV, XLSX, GeoJSON, KML o SHP segun la fuente.
- Mapa: Leaflet o MapLibre.
- IA: proveedor configurable por `LLM_BASE_URL`, `LLM_API_KEY` y `LLM_MODEL`.
- Geocodificacion: servicio compatible con CABA y con politica de uso adecuada.
- Hosting: Vercel para frontend y Render, Railway o equivalente para backend.

No es necesario implementar una arquitectura RAG compleja para el MVP si las fuentes pueden normalizarse previamente. Debe dejarse una interfaz de recuperacion extensible para incorporar documentos citables en el futuro.

## 16. Seguridad y trazabilidad

- No enviar datos personales innecesarios al proveedor de IA.
- No exponer claves de API en el frontend.
- Registrar proveedor y modelo utilizados.
- Registrar la version del prompt o esquema de interpretacion.
- Conservar la consulta original y la salida estructurada validada.
- Registrar fuentes utilizadas, fecha de ingesta y fecha de respuesta.
- Aplicar limites de solicitudes y manejo de errores.
- Sanitizar enlaces y contenido recibido de fuentes externas.

## 17. Pruebas necesarias

### Casos funcionales

- “Quiero abrir un local de ropa en Av. Corrientes 2500”.
- “Quiero poner una cafeteria en Palermo”.
- Variantes con errores ortograficos y lenguaje coloquial.
- Consulta con direccion incompleta.
- Consulta con actividad desconocida.
- Consulta fuera de CABA.
- Pregunta de seguimiento sobre documentacion o pasos.

### Validaciones de datos

- La actividad se corresponde con el catalogo.
- La direccion se geocodifica correctamente.
- La comuna y el barrio corresponden a las coordenadas.
- Cada requisito tiene una fuente oficial.
- Cada oficina tiene coordenadas validas.
- El frontend dibuja correctamente los marcadores.
- La fecha de actualizacion se muestra correctamente.

### Pruebas negativas

- El modelo no agrega requisitos inexistentes.
- El modelo no inventa oficinas ni coordenadas.
- Una fuente caida produce una respuesta parcial claramente informada.
- Una direccion ambigua requiere confirmacion.
- Una actividad fuera de alcance no genera una respuesta oficial falsa.

## 18. Criterios de aceptacion

1. El sistema interpreta una consulta en espanol y separa intencion, actividad y direccion.
2. La actividad se valida contra un catalogo controlado.
3. La direccion se geocodifica y puede ser confirmada por la persona usuaria.
4. El sistema determina comuna, barrio y jurisdiccion aplicable dentro de CABA.
5. Se integran al menos tres fuentes oficiales viables.
6. Los requisitos, documentos y pasos se filtran por actividad y ubicacion.
7. La respuesta incluye tramites online y oficinas fisicas cuando existen.
8. Las oficinas y la ubicacion consultada devuelven latitud y longitud para el mapa.
9. Cada dato relevante mantiene origen y fecha de actualizacion.
10. La IA no agrega informacion sin respaldo.
11. Se manejan estados de informacion faltante, parcial, desactualizada y no disponible.
12. El flujo completo se valida mediante pruebas end-to-end contra las fuentes originales.

## 19. Fuera de alcance inicial

- Resolver automaticamente la normativa de todos los municipios del pais.
- Consultar indiscriminadamente la web abierta.
- Permitir que el modelo genere requisitos o coordenadas sin validacion.
- Cubrir todas las actividades comerciales antes de validar el caso piloto.
- Implementar personalizacion, alertas e historial avanzado antes de estabilizar el MVP.
