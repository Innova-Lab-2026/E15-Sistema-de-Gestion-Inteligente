# Documentación — InobaLab TECBA API

Onboarding del backend MVP de orientación ciudadana (CABA).

Swagger en vivo (con la API levantada): [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

## Orden de lectura sugerido

1. [overview.md](overview.md) — qué problema resuelve el API y flujo de una consulta  
2. [setup.md](setup.md) — cómo levantar DB + API en local  
3. [endpoints.md](endpoints.md) — catálogo de endpoints v1  
4. [fuentes-y-datos.md](fuentes-y-datos.md) — USIG, epok, BA Data, trámites, oficinas  
5. [snapshots-y-seed.md](snapshots-y-seed.md) — scripts `fetch_*`, seed y qué necesita (o no) uvicorn  

## Documentos de contexto / equipo

| Documento | Para qué |
|---|---|
| [guia-equipo-backend.md](guia-equipo-backend.md) | Roles, stack y etapas del subequipo backend |
| [fuentes-pruebas.md](fuentes-pruebas.md) | Pruebas de acceso a fuentes oficiales |
| [arquitectura-ia.md](arquitectura-ia.md) | Flujo IA, contratos JSON |
| [plan-implementacion.md](plan-implementacion.md) | Plan técnico por etapas |

## Pruebas

- Colección Postman: [`../postman/README.md`](../postman/README.md)
- Checklist del agente (interno): [`.cursor/agent/PLAN-EJECUCION.md`](../.cursor/agent/PLAN-EJECUCION.md)
