# Plan del Sistema de Gestión Inteligente — TECBA

Plataforma web inteligente de consulta y orientación ciudadana, con información territorial, de trámites y de contexto de la Ciudad de Buenos Aires.
Documento derivado del reporte *Sistema de Gestión Inteligente - TECBA* (23 páginas). Organizado en sprints de 2 semanas y por equipos: **Todos/Coordinación, UX/UI, Frontend, Backend, BI-Data-ML y QA**.

---

## 1. Resumen y contexto

- TECBA impulsa una **plataforma web inteligente** que combina datos territoriales y de trámites de la Ciudad para **orientar a la ciudadanía** frente a una necesidad concreta.
- Una persona expresa una necesidad en **lenguaje natural** junto con su **ubicación** y la plataforma le responde, sobre un **mapa interactivo**, qué debe hacer: trámites, requisitos, documentación, pasos e información territorial relevante.
- **Caso emblemático:** *"Quiero abrir una cafetería en Av. Corrientes 2500. ¿Qué tengo que hacer?"*
- La **IA actúa como capa de consulta e interpretación**: no reemplaza ni contradice las fuentes oficiales. Toda la información respaldada proviene de las fuentes integradas.
- Se entrega un **MVP validado en 12 semanas (6 sprints)** para un caso piloto, con una arquitectura extensible a futuro.

## 2. Problemática

- La información que necesita la ciudadanía (trámites, requisitos, habilitaciones, normativa territorial) está **dispersa en múltiples sistemas** del Gobierno de la Ciudad, en distintos formatos y con lógicas diferentes.
- La persona no siempre sabe qué consultar, en qué orden, ni qué documentación reunir para iniciar una actividad.
- Falta un **punto único de consulta** que integre fuentes, contextualice por ubicación y explique de forma clara y sencilla los pasos a seguir.

## 3. Solución propuesta y flujo general

**Caso MVP:** el inicio de una **nueva actividad comercial** en la Ciudad.

Flujo general de la plataforma:

```
Necesidad ciudadana + ubicación
  → Interpretación de la actividad y el lugar (IA)
  → Consulta a las fuentes relevantes
  → Integración de información territorial + contexto + trámites
  → Orientación contextualizada (requisitos, documentación, pasos)
  → Visualización territorial (mapa interactivo)
  → Profundización (preguntas de seguimiento con IA)
```

La **arquitectura** sigue esa cadena (necesidad → ubicación → integración de fuentes → interpretación → orientación contextualizada → visualización territorial) y permite **sumar nuevos casos de uso** sin modificar la lógica central.

## 4. Alcance MVP

- Caso de uso piloto: **inicio de una nueva actividad comercial**.
- Resolver el **camino feliz** completo: de la consulta a la orientación final.
- Integrar **al menos 3 fuentes** de información.
- Información **territorial** y de **trámites** presentada conjuntamente.
- **Mapa interactivo** con la ubicación consultada y capas de datos territoriales.
- **Consulta en lenguaje natural con IA** sobre el caso piloto (contexto = solo información integrada y validada).
- **Trazabilidad de fuentes** (origen y fecha de actualización de cada dato).
- Preguntas de seguimiento básicas.
- Dejar preparada la solución para escalar a más actividades, trámites y fuentes (punto único de consulta territorial).

## 5. Fuentes de información

- Fuentes territoriales y de datos abiertos consideradas: **IDECABA, BA Data, Ciudad 3D** y servicios digitales del Gobierno de la Ciudad.
- Trámites: **API oficial cuando exista** o mecanismo de consulta definido durante el relevamiento.
- Formatos posibles: **PDF, CSV, XLSX, KML, SHP, JSON** (según la fuente).
- Durante el MVP se **evalúa el acceso real** de cada fuente candidata antes de comprometerla.
- La información de trámites, territorio y requisitos **debe provenir de las fuentes integradas**; el modelo de IA **no es fuente de verdad**.

## 6. Funcionalidades clave

1. **Consulta en lenguaje natural con IA**: interpreta la actividad y la ubicación de la consulta.
2. **Recuperación e integración de fuentes**: relaciona territorio, contexto y trámites.
3. **Orientación clara**: requisitos, documentación, pasos a seguir e información territorial relevante, jerarquizados.
4. **Mapa interactivo**: muestra la ubicación, capas/datos territoriales y permite explorar puntos, zonas o capas.
5. **Preguntas de seguimiento**: profundizar la consulta dentro del caso piloto.
6. **Trazabilidad de la información**: identificar qué fuentes respaldan cada respuesta; conservar metadatos de origen y fecha de actualización; mantener diferenciada la información de cada fuente; **no presentar como oficial información sin respaldo**.
7. **Estados de información**: manejo de datos incompletos, desactualizados o no disponibles.
8. **Evolución planificada**: historial de consultas, personalización, alertas, reportes e integraciones con servicios digitales del Gobierno; extensión a nuevos casos de uso (consulta territorial por punto/zona: IDECABA, BA Data, Ciudad 3D).

## 7. Equipos y responsabilidades

| Equipo | Responsabilidades principales |
|---|---|
| **Todos / Coordinación** | Revisar problema, solución y requisitos; definir caso piloto y camino feliz; roles, dinámica y tablero; alinear decisiones semanales; priorizar ajustes. |
| **UX/UI (Diseño)** | Recorridos y flujos; wireframes; pantallas; estados (carga, error, falta de info); jerarquía de requisitos/documentación/pasos/territorio/fuentes; accesibilidad y claridad; experiencia de mapa y consulta con IA. |
| **Frontend** | App web (React/Next.js); estructura de navegación; interfaz de consulta; mapa interactivo; componentes de resultados, trámites y fuentes; integración con el backend. |
| **Backend** | APIs (Python + FastAPI); integración de fuentes; geocodificación; base de datos; respuesta estructurada para el frontend; servicio de IA y contexto; trazabilidad y metadatos; manejo de errores. |
| **BI, Data & ML** | Selección y análisis de ≥3 fuentes; normalización; relaciones actividad/ubicación/territorio/trámites; capas del mapa; estructura de datos para IA; calidad, consistencia y documentación de transformaciones. |
| **QA** | Estrategia de testing; casos de prueba; testing end-to-end; comparación contra fuentes originales; validación de IA sin info no respaldada; registro de riesgos y bugs. |

## 8. Plan por fases

Legenda entregas semanales: ✅ Entregable · ❎ Dependencia.

### Sprint Planning — Semana 0 · Organización y caso piloto

> **Objetivo:** organizar el equipo, definir el caso piloto y validar inicialmente las fuentes del recorrido del MVP.

| Equipo | Tareas |
|---|---|
| Todos | Revisar problemática, solución, funcionalidades y requisitos del MVP; definir roles, dinámica de trabajo y tablero; confirmar el caso de uso piloto (inicio de actividad comercial); definir qué resuelve el camino feliz; identificar información necesaria. |
| UX/UI | Definir el recorrido general (consulta → ubicación → orientación → mapa → profundización); identificar pantallas principales; criterios iniciales de claridad, accesibilidad y presentación. |
| Frontend | Configurar proyecto, repositorio y entorno; estructura inicial de navegación y componentes; evaluar técnicamente la integración del mapa interactivo. |
| Backend | Configurar backend y base de datos; arquitectura inicial para consultas, fuentes, ubicaciones y respuestas; analizar mecanismos de acceso a las fuentes candidatas; evaluar servicio de geocodificación. |
| BI, Data & ML | Identificar al menos 3 fuentes potenciales; analizar estructura, disponibilidad y calidad; determinar cómo relacionar actividad, ubicación, territorio y trámites; identificar campos/dimensiones comunes. |
| QA | Definir estrategia inicial de testing; identificar escenarios críticos del camino feliz; criterios para validar exactitud de datos, ubicación y respuestas. |

**✅ Entregable:** equipo y roles definidos · caso piloto seleccionado · camino feliz inicial · 3 fuentes candidatas · arquitectura inicial acordada · estrategia de mapa y geocodificación evaluada · repositorios y entornos configurados.
**❎ Dependencias:** caso de uso priorizado · disponibilidad de fuentes públicas · acceso a herramientas y servicios · validación inicial de mecanismos de consulta.

### Sprint 1 · Exploración — Semanas 1 y 2

> **Objetivo Sem 1:** validar que las fuentes permiten responder el caso de uso y construir técnicamente la relación entre actividad, ubicación y trámites.
> **Objetivo Sem 2:** construir la primera versión funcional del recorrido *consulta + ubicación + información integrada*.

| Equipo | Semana 1 | Semana 2 |
|---|---|---|
| Todos | Desglosar la pregunta del caso piloto en necesidades de información; definir qué resultado debe recibir la persona; qué aporta cada fuente. | Validar qué información mínima debe contener la respuesta; definir el orden del camino feliz; confirmar las 3 fuentes definitivas del MVP. |
| UX/UI | Diseñar el flujo inicial de consulta; wireframes de búsqueda, ingreso de ubicación y presentación de resultados; definir cómo mostrar requisitos, documentación y pasos. | Completar wireframes del camino feliz; diseñar estados de carga, error y falta de información; primera versión de mapa y de orientación paso a paso. |
| Frontend | Implementar la estructura base de la plataforma; primera interfaz de consulta; preparar componente inicial de ubicación/mapa. | Implementar ingreso de actividad y ubicación; integrar mapa básico; mostrar ubicación consultada; primera estructura visual de requisitos, documentación y pasos. |
| Backend | Primeras conexiones/procesos de lectura sobre las fuentes; prueba de geocodificación de direcciones; estructura común para organizar la información recuperada. | Implementar servicios iniciales para recuperar información de las fuentes; procesar actividad y ubicación; relacionar primeros resultados; preparar respuesta estructurada para el frontend. |
| BI, Data & ML | Analizar las tres fuentes; identificar variables territoriales, de actividad y de trámites; primeras transformaciones y relaciones; documentar problemas de calidad o disponibilidad. | Normalizar la información de las 3 fuentes; primeras relaciones entre datos territoriales, contexto y trámites; validar consistencia para el caso piloto. |
| QA | Validar acceso y respuesta de las fuentes; casos de prueba para direcciones y consultas del caso piloto; registrar riesgos o limitaciones. | Testear consultas válidas e inválidas; validar ubicación y datos mostrados; comparar respuesta integrada con fuentes originales; definir criterios de aceptación del camino feliz. |

**✅ Entregable (S1):** 3 fuentes técnicamente evaluadas · relación actividad-ubicación-trámites definida · primera dirección geocodificada · wireframes principales · interfaz base de consulta iniciada · riesgos técnicos documentados.
**❎ Dependencias (S1):** fuentes identificadas en Semana 0 · acceso efectivo a la información · caso piloto y resultado esperado definidos.
**✅ Entregable (S2):** 3 fuentes definitivas integradas inicialmente · consulta de actividad y ubicación operativa · mapa básico funcional · primera información territorial · primera respuesta estructurada sobre trámites y requisitos.
**❎ Dependencias (S2):** camino feliz definido de punta a punta · fuentes técnicamente viables · geocodificación funcionando · relaciones entre datos identificadas · información oficial suficiente.

### Sprint 2 · Ideación — Semanas 3 y 4

> **Objetivo Sem 3:** desarrollar la primera experiencia territorial integrada y transformar los datos procesados en información clara y útil para la ciudadanía.
> **Objetivo Sem 4:** completar el camino feliz del caso piloto y consolidar la presentación integrada de trámites, territorio y contexto.

| Equipo | Semana 3 | Semana 4 |
|---|---|---|
| Todos | Validar la estructura final de la respuesta; qué información territorial es relevante para la actividad; acordar capas/datos del mapa; revisar orden de requisitos, documentación y pasos. | Revisar el recorrido completo (necesidad → orientación final); validar que la información responda a la consulta ciudadana; definir qué queda fuera cuando no es relevante; acordar cómo se muestra el respaldo de las fuentes. |
| UX/UI | Diseñar la experiencia de resultados; convivencia de mapa, información territorial y orientación; jerarquías para requisitos/documentación/pasos/territorio/fuentes; estados de info incompleta. | Ajustar el recorrido completo; navegación entre mapa, pasos y detalle; incorporar referencias visibles a fuentes oficiales; mejorar claridad del camino feliz. |
| Frontend | Pantalla principal de resultados; ubicación en el mapa; primeras capas/datos territoriales; componentes de requisitos, documentación y pasos; vincular cada bloque con su contexto. | Recorrido completo de resultados; interacción básica con el mapa; consultar info asociada a puntos, zonas o capas; mostrar fuentes y origen; ajustar requisitos, documentación y próximos pasos. |
| Backend | Consolidar servicios de las 3 fuentes; relación ubicación-actividad-información territorial; endpoints para mapa, trámites y contexto; estructura de respuesta para el camino feliz. | Consolidar integración de las 3 fuentes; mejorar reglas de relación actividad-ubicación-trámites; metadatos de origen y actualización; preparar estructura para la futura capa de IA. |
| BI, Data & ML | Procesar la información territorial; validar relaciones entre fuentes; preparar capas/variables del mapa; comprobar consistencia ubicación-actividad-resultados. | Validar resultados para distintos escenarios del caso piloto; revisar calidad y consistencia territorial; documentar reglas de relación y transformaciones; preparar info estructurada para consultas en lenguaje natural. |
| QA | Validar información territorial mostrada; comparar resultados con fuentes originales; testear direcciones dentro del alcance; registrar inconsistencias geográficas o de datos. | Testing completo del camino feliz; validar que cada bloque tenga respaldo en su fuente; escenarios de falta de datos o ubicación no reconocida; validar mapa e interacción. |

**✅ Entregable (S3):** primera experiencia territorial integrada · mapa con ubicación funcional · información de las 3 fuentes relacionada · requisitos, documentación y pasos visibles · primera versión visual del camino feliz.
**❎ Dependencias (S3):** 3 fuentes integradas inicialmente · geocodificación operativa · datos territoriales disponibles · estructura de respuesta definida.
**✅ Entregable (S4):** camino feliz funcional sin IA · 3 fuentes integradas y relacionadas · info territorial y de trámites presentada conjuntamente · mapa interactivo operativo · requisitos/documentación/pasos organizados · trazabilidad básica de fuentes.
**❎ Dependencias (S4):** integración territorial de Semana 3 · 3 fuentes estables · información oficial suficiente · mapa y geocodificación funcionando.

### Sprint 3 · Desarrollo (Primer MVP) — Semanas 5 y 6

> **Objetivo Sem 5:** incorporar la primera versión de consulta mediante IA, usando como contexto **únicamente la información integrada y validada** del caso piloto.
> **Objetivo Sem 6:** integrar todas las funcionalidades y alcanzar la **primera versión completa del MVP**.

| Equipo | Semana 5 | Semana 6 |
|---|---|---|
| Todos | Definir qué preguntas podrá interpretar la IA; acordar qué información podrá usar; criterios para evitar respuestas no respaldadas por fuentes oficiales; cómo manejar consultas ambiguas o fuera de alcance. | Revisar el recorrido completo (consulta → orientación final); validar que el caso piloto cumpla los requisitos de TECBA; detectar funcionalidades incompletas; priorizar ajustes para la segunda mitad. |
| UX/UI | Diseñar el espacio de consulta en lenguaje natural; presentación de respuestas, fuentes y datos territoriales; estados de carga, error y falta de info; experiencia clara para preguntas de seguimiento. | Revisar navegación y experiencia completa; ajustar consulta, mapa, orientación, fuentes y seguimiento; unificar estados, mensajes y comportamientos; validar comprensión para quien no conoce los sistemas del Gobierno. |
| Frontend | Interfaz de consulta con IA; respuesta dentro del contexto del caso; integrar respuesta con mapa, requisitos, documentación y pasos; referencias visibles a fuentes. | Integrar consulta, mapa, info territorial, trámites e IA; consolidar navegación entre resultados y detalle; mejorar visualización de requisitos, documentación, pasos y fuentes; corregir inconsistencias de integración. |
| Backend | Integrar el servicio de IA seleccionado; preparar el contexto desde la información procesada; extraer actividad y ubicación de la consulta; controlar que la respuesta use solo info de las fuentes; lógica básica de preguntas de seguimiento. | Consolidar la integración de las 3 fuentes; integrar procesamiento territorial, trámites, geocodificación e IA en un mismo flujo; mejorar manejo de errores/ausencia de info; consolidar trazabilidad básica. |
| BI, Data & ML | Preparar la info estructurada que usará la IA; definir consultas y respuestas esperadas; validar consistencia respuesta-datos territoriales-trámites; identificar casos sin info suficiente. | Validar relaciones entre las 3 fuentes; revisar consistencia territorial y de trámites; verificar que las respuestas de IA correspondan a los datos; ajustar reglas o transformaciones. |
| QA | Testear consultas simples, ambiguas y fuera de alcance; validar extracción de actividad y ubicación; comparar respuestas con fuentes originales; verificar que la IA **no agregue** info no respaldada. | Primer testing end-to-end; validar el caso piloto de punta a punta; probar distintas consultas dentro del alcance; registrar y priorizar bugs técnicos y de contenido. |

**✅ Entregable (S5):** primera consulta con IA funcionando · identificación de actividad y ubicación operativa · respuestas contextualizadas sobre el caso piloto · preguntas de seguimiento básicas · referencias a fuentes visibles · primer conjunto de consultas validado.
**❎ Dependencias (S5):** consulta de actividad/ubicación funcionando · 3 fuentes integradas · info territorial disponible · mapa interactivo operativo (de Sprints previos).
**✅ Entregable (S6):** primera versión integral del MVP · consulta de actividad y ubicación funcionando · 3 fuentes integradas · info territorial disponible · mapa interactivo operativo · camino feliz completo · consulta con IA integrada · preguntas de seguimiento · trazabilidad de fuentes · primer testing completo.
**❎ Dependencias (S6):** funcionalidades de semanas anteriores integradas · 3 fuentes estables · mapa y geocodificación funcionando · información oficial suficiente · integración de IA operativa.

### Sprint 4 · Desarrollo (Confiabilidad y trazabilidad) — Semanas 7 y 8

> **Objetivo Sem 7:** mejorar la confiabilidad de la información integrada y consolidar la **trazabilidad entre consulta, respuesta y fuentes oficiales**.
> **Objetivo Sem 8:** fortalecer la experiencia de consulta con IA y **consolidar el MVP** para la etapa de iteración.

| Equipo | Semana 7 | Semana 8 |
|---|---|---|
| Todos | Revisar qué información debe conservarse sobre cada fuente; cómo comunicar info incompleta, desactualizada o no disponible; acordar criterios para diferenciar datos territoriales, de contexto y de trámites. | *(Iteración)* Revisar resultados de la validación; priorizar mejoras de confiabilidad y experiencia para la fase final. |
| UX/UI | Mejorar visualización del origen de la información; estados para info disponible/incompleta/no encontrada; presentación de fuentes en la orientación final; vínculo mapa-datos-trámites. | Validación de trazabilidad en la experiencia; refinamiento de la respuesta respaldada y de los estados. |
| Frontend | Referencias claras a fuentes utilizadas; mejores estados de carga/error/falta de info; acceder desde una respuesta al detalle que la respalda; ajustar capas y datos territoriales del mapa. | Pulido de la experiencia de consulta con IA; navegación y acceso a detalle de fuentes. |
| Backend | Consolidar metadatos de fuentes; registrar origen y fecha de actualización; mejorar validaciones sobre info recuperada; gestionar respuestas parciales (fuente no disponible); reforzar relación datos-utilizados ↔ respuesta-generada. | Consolidar trazabilidad completa consulta → respuesta → fuentes; robustez de la capa de IA. |
| BI, Data & ML | Validar exactitud de metadatos; consistencia dato-fuente; completitud de la información del caso piloto. | Validar que la consulta con IA mantenga coherencia con los datos disponibles. |
| QA | Verificar trazabilidad (toda respuesta vinculada a su fuente); testing de estados de info faltante; validar contra fuentes originales. | Testing de confiabilidad; registrar hallazgos de la fase de iteración. |

**✅ Entregable (S7):** trazabilidad consolidada (origen + fecha por dato) · estados de información disponibles/incompleta/no encontrada · acceso al detalle que respalda cada respuesta · respuestas parciales gestionadas.
**✅ Entregable (S8):** MVP consolidado y estable para iterar (testing + criterios de aceptación completos).

### Sprint 5 · Iteración / Release Candidate — Semanas 9 y 10

> **Objetivo:** testing integral, priorizar y corregir bugs, y optimizar la información y la experiencia.

| Equipo | Tareas clave |
|---|---|
| Todos | Revisar resultados del testing integral; priorizar correcciones de bugs e inconsistencias de contenido/experiencia. |
| UX/UI | Ajustar flujos, jerarquías y estados según hallazgos; refinamientos de accesibilidad y claridad. |
| Frontend | Corregir bugs de integración, mapa y componentes; optimizar rendimiento y visualización. |
| Backend | Corregir bugs de servicios, geocodificación e IA; robustecer manejo de errores y respuestas parciales. |
| BI, Data & ML | Actualizar/normalizar datos afectados; ajustar reglas de relación y transformaciones. |
| QA | Testing integral de regresión; ejecutar el conjunto completo de casos de prueba; validar criterios de aceptación del MVP. |

**✅ Entregable:** Release Candidate del MVP (sin bugs críticos conocidos) · suite de testing ejecutada · criterios de aceptación validados.

### Sprint 6 · Cierre — Semanas 11 y 12

> **Objetivo:** validación final, despliegue, documentación técnica y funcional, y presentación del proyecto.

| Equipo | Tareas clave |
|---|---|
| Todos | Aprobación final del caso piloto; preparación de la presentación/demo end-to-end. |
| UX/UI | Entrega de guías de diseño y recorridos finales documentados. |
| Frontend | Despliegue del frontend (Vercel); verificación final de la experiencia. |
| Backend | Despliegue del backend y base de datos; verificación de endpoints y trazabilidad. |
| BI, Data & ML | Documentación de fuentes, reglas de relación y transformaciones. |
| QA | Validación final en el entorno desplegado; cierre de casos de prueba; documentación de riesgos residuales. |

**✅ Entregable:** MVP desplegado y operativo · documentación técnica y funcional · demo end-to-end funcional · lecciones aprendidas y próximos pasos de escalabilidad.

---

## 9. Tecnologías, licencias y escalabilidad

### Stack recomendado para el MVP

| Necesidad | Tecnologías / herramientas |
|---|---|
| Desarrollo web | React / Next.js |
| Lenguaje frontend | JavaScript / TypeScript |
| Backend / APIs | Python + FastAPI |
| Base de datos | PostgreSQL / Supabase |
| Información geoespacial | PostgreSQL + PostGIS |
| Autenticación | Supabase Auth / JWT |
| Procesamiento de datos | Python / Pandas |
| Carga de datos estructurados | CSV / XLSX / JSON |
| Procesamiento geográfico | GeoPandas |
| Formatos territoriales | GeoJSON / KML / SHP (según fuentes) |
| Mapa interactivo | Leaflet / MapLibre GL / Mapbox (según necesidades y licenciamiento) |
| Geocodificación | Servicio compatible para transformar direcciones en coordenadas |
| Integración de fuentes | APIs REST / procesamiento de datasets públicos |
| Info. de trámites | API oficial (cuando exista) / mecanismo definido en relevamiento |
| Inteligencia Artificial | API de modelo LLM de terceros (Gemini Flash + OpenRouter como fallback), proveedor abstraído por variables de entorno |
| Contexto para IA | Recuperación de info procesada + prompts estructurados |
| Trazabilidad | Metadatos de fuentes, origen y fecha de actualización |
| Testing de APIs | Postman |
| Diseño UX/UI | Figma |
| Flujos y arquitectura | FigJam / Miro |
| Gestión de QA | Jira + Zephyr (o equivalente) |
| Control de versiones | Git + GitHub |
| Hosting frontend | Vercel |
| Hosting backend | Render / Railway |
| BD y almacenamiento | Supabase |

### Criterio técnico para la IA

- Para el MVP **no es necesario implementar una arquitectura RAG compleja** si las fuentes seleccionadas pueden procesarse y estructurarse previamente.
- La IA funciona como capa de: **interpretación de la consulta → identificación de actividad y ubicación → recuperación de información relevante → organización y explicación de la respuesta**.
- Los datos de trámites, territorio y requisitos **provienen de las fuentes integradas**; el modelo **no es fuente de verdad** y nunca debe contradecir las fuentes oficiales.

### Decisión de IA: proveedor y estrategia

- **Ollama / self-hosted descartado para el MVP:** requiere GPU y servidor propio; los planes free de Render/Railway no ofrecen GPU, por lo que no es viable para el despliegue inicial. Solo se justificaría con volúmenes muy altos (más de ~200–500M tokens/mes) o requisitos de privacidad/data residency, que no aplican a este MVP.
- **Modelo**: API de terceros con API key, sin infraestructura propia.
- **Free tiers sin tarjeta para pruebas:**
  - **Google AI Studio (Gemini Flash):** modelo principal por mejor calidad y español para interpretar actividad y ubicación; contexto de hasta 1M de tokens. ⚠️ El free tier entrena con los datos enviados (no aplica en UE/UK/EEA); usar solo datos no sensibles en desarrollo.
  - **Groq (Llama 3.3 70B):** alternativa rápida (velocidad muy alta), no entrena con los datos.
  - **OpenRouter:** router con una sola key, 20+ modelos `:free` y **failover automático** entre proveedores → respaldo cuando se agota la cuota del proveedor principal.
  - Otras opciones evaluadas como respaldo: Cerebras, Mistral (Experiment), GitHub Models, NVIDIA NIM, Cloudflare Workers AI.
- **Límites a manejar:** RPM y requests/día propios de cada free tier; agregar respaldo por saturación de cuota.
- **Abstracción en el código:** el proveedor se configura por variables de entorno (`LLM_BASE_URL`, `LLM_API_KEY`, `LLM_MODEL`); desarrollo con free tier y producción con el plan pay-as-you-go del mismo proveedor sin tocar la lógica.

### Licencias y escalabilidad

- Priorizar **soluciones open source y planes gratuitos** para el MVP.
- Pagar solo cuando crezca el volumen: **geocodificación, mapas, IA y almacenamiento** suelen tener costo por uso.
- La IA pasa de free tier a **pago por uso** cuando crece el volumen; los proveedores elegidos (Gemini Flash / Groq / OpenRouter) son de bajo costo por token.
- La arquitectura (necesidad → ubicación → integración → interpretación → orientación → visualización) permite **incorporar nuevos casos de uso y fuentes sin modificar la lógica central** (punto único de consulta territorial: IDECABA, BA Data, Ciudad 3D y otras).

## 10. Criterios de aceptación del MVP

1. **Caso piloto resuelto de punta a punta:** "Quiero abrir una actividad comercial en una dirección. ¿Qué tengo que hacer?" con orientación clara (trámites, requisitos, documentación y pasos).
2. **Al menos 3 fuentes oficiales integradas**, con trazabilidad (origen y fecha de actualización de cada dato).
3. **Mapa interactivo operativo:** muestra la ubicación consultada y capas de datos territoriales.
4. **Consulta en lenguaje natural con IA**: interpreta actividad y ubicación; respuestas contextualizadas y comprensibles para la ciudadanía.
5. **Preguntas de seguimiento básicas** dentro del caso piloto.
6. **La IA no agrega información sin respaldo** ni reemplaza a las fuentes oficiales (toda respuesta vinculada a su fuente).
7. **Estados de información** correctos para datos incompletos, desactualizados o no disponibles (incluida ubicación no reconocida).
8. **Testing end-to-end** realizado, con comparación de resultados contra las fuentes originales.
9. **Documentación técnica y funcional** entregada y **demo end-to-end** funcional en el entorno desplegado.