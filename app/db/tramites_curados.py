"""Tramites GCBA curados a mano (sin API oficial).

Fuente primaria:
https://www.buenosaires.gob.ar/tramites/como-habilitar-tu-local-comercial-en-la-ciudad

Regla: todo texto de orientacion lleva url_fuente. No inventar requisitos.
Fecha de curaduria: 2026-09-30.
"""

from __future__ import annotations

from datetime import datetime, timezone

CURATED_AT = datetime(2026, 9, 30, tzinfo=timezone.utc)

URL_GUIA_LOCAL = (
    "https://www.buenosaires.gob.ar/tramites/"
    "como-habilitar-tu-local-comercial-en-la-ciudad"
)
URL_HABILITACION = (
    "https://www.buenosaires.gob.ar/tramites/habilitacion-de-actividad-economica"
)
URL_HABILITACION_EXPRES = (
    "https://www.buenosaires.gob.ar/tramites/"
    "habilitacion-de-actividad-economica-expres"
)
URL_CIUDAD_3D = "https://ciudad3d.buenosaires.gob.ar/"
URL_MIBA = "https://www.buenosaires.gob.ar/tramites"

# Rubros piloto con guia comercial curada (codes API)
PILOT_COMMERCIAL_CODES: frozenset[str] = frozenset(
    {
        "rubro_102",  # gastronomia
        "rubro_471",  # alimentacion para llevar
        "rubro_16",  # comercio minorista no comestibles
        "rubro_309",  # ferreteria industrial
        "rubro_66",  # farmacia
        "rubro_137",  # supermercado
        "rubro_169",  # maxikiosco
        "rubro_245",  # kiosco
        "rubro_4",  # pintureria
        "rubro_136",  # animales domesticos
    }
)

# Categorias epok que pueden usar la guia de local comercial como orientacion
COMMERCIAL_EPOK_CATEGORY_IDS: frozenset[int] = frozenset({1})


def commercial_habilitation_guide(activity_name: str, rubro_id: int | None) -> dict:
    """Contenido curado alineado a la guia GCBA de habilitar local comercial."""
    rubro_txt = f" (rubro epok {rubro_id})" if rubro_id is not None else ""
    return {
        "title": f"Habilitacion de local comercial - {activity_name}",
        "description": (
            f"Orientacion curada para {activity_name}{rubro_txt} en CABA, "
            "basada en la guia oficial GCBA "
            "\"Como habilitar tu local comercial en la Ciudad\". "
            f"Fuente: {URL_GUIA_LOCAL} "
            f"(curado {CURATED_AT.date().isoformat()}). "
            "Confirmar siempre en el sitio oficial: condiciones, superficies "
            "y documentos pueden cambiar."
        ),
        "status": "available",
        "documents": [
            {
                "name": "Cuenta miBA / identidad digital",
                "details": (
                    "Perfil digital en miBA para iniciar tramites. "
                    f"Ver guia: {URL_GUIA_LOCAL}"
                ),
                "url_fuente": URL_GUIA_LOCAL,
            },
            {
                "name": "Apoderamientos / Clave Ciudad (si es persona juridica)",
                "details": (
                    "Representante legal ante ARCA: Clave Ciudad AGIP y vinculacion "
                    "con la persona juridica para apoderamientos en TAD."
                ),
                "url_fuente": URL_GUIA_LOCAL,
            },
            {
                "name": "Anexo tecnico de profesional matriculado (si no es expres)",
                "details": (
                    "Arquitecto, ingeniero o maestro mayor de obras matriculado en CABA "
                    "verifica condiciones edilicias (Codigo de Edificacion / Urbanismo)."
                ),
                "url_fuente": URL_HABILITACION,
            },
            {
                "name": "Certificado de Aptitud Ambiental (CAA)",
                "details": (
                    "Solicitar antes o durante la Autorizacion de Actividad Economica."
                ),
                "url_fuente": URL_HABILITACION,
            },
            {
                "name": "Sistema de Autoproteccion (segun grupo 1/2/3)",
                "details": (
                    "Grupo 1: declaracion jurada. Grupos 2/3: aprobacion del sistema "
                    "segun cuadro de clasificacion de establecimientos."
                ),
                "url_fuente": URL_GUIA_LOCAL,
            },
        ],
        "steps": [
            {
                "order": 1,
                "title": "Crear cuenta en miBA",
                "description": (
                    "Registra o inicia sesion en miBA para tramitar en linea."
                ),
                "url_fuente": URL_GUIA_LOCAL,
            },
            {
                "order": 2,
                "title": "Gestionar apoderamientos necesarios",
                "description": (
                    "Si actuas por persona juridica, obtene Clave Ciudad AGIP y "
                    "vincula al representante para validar apoderamientos en TAD."
                ),
                "url_fuente": URL_GUIA_LOCAL,
            },
            {
                "order": 3,
                "title": "Revisar normativa del lote (Ciudad 3D)",
                "description": (
                    "Verifica que la actividad este permitida en la direccion "
                    "(mixturas, usos, superficies). Codigo Urbanistico Ley 6099/2018."
                ),
                "url_fuente": URL_CIUDAD_3D,
            },
            {
                "order": 4,
                "title": "Consulta de usos / visados especiales (si aplica)",
                "description": (
                    "Factibilidad de uso, publicidades, marquesinas/toldos o antenas "
                    "en areas o inmuebles con proteccion especial."
                ),
                "url_fuente": URL_GUIA_LOCAL,
            },
            {
                "order": 5,
                "title": "Autorizacion de Actividad Economica",
                "description": (
                    "Si el local tiene menos de 200 m2, evaluar habilitación exprés. "
                    "Si no cumple, tramite comun con profesional matriculado + CAA."
                ),
                "url_fuente": URL_HABILITACION,
                "url_fuente_expres": URL_HABILITACION_EXPRES,
            },
            {
                "order": 6,
                "title": "Sistema de Autoproteccion",
                "description": (
                    "Clasifica el establecimiento (Grupo 1/2/3) y completa DDJJ "
                    "o aprobacion segun corresponda."
                ),
                "url_fuente": URL_GUIA_LOCAL,
            },
        ],
        "source_ids": [
            "source-001",
            "source-005",
            "source-006",
            "source-007",
            "source-004",
        ],
    }


def uses_curated_commercial_guide(
    *, activity_code: str, epok_category_id: int | None
) -> bool:
    if activity_code in PILOT_COMMERCIAL_CODES:
        return True
    return epok_category_id in COMMERCIAL_EPOK_CATEGORY_IDS
