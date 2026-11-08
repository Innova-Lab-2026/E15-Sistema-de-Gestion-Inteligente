"""Add the "05 Clarifications" folder to the Postman collection: one request per `reason` (B12).

Run from Backend/: python scripts/update_postman_clarifications.py
"""

from __future__ import annotations

import json
from pathlib import Path

p = Path("postman/InobaLab-TECBA.postman_collection.json")
data = json.loads(p.read_text(encoding="utf-8"))

FOLDER = "05 Clarifications"
NO_CODES = [
    "pm.test('message sin codigos internos', function () {",
    "  var j = pm.response.json();",
    "  pm.expect(j.message).to.be.a('string');",
    "  pm.expect(j.message).to.not.match(/rubro_|activity_|location_|_out_of_scope/);",
    "});",
]


def request(name, url, body, description, tests):
    return {
        "name": name,
        "event": [{"listen": "test", "script": {"type": "text/javascript", "exec": tests}}],
        "request": {
            "method": "POST",
            "header": [{"key": "Content-Type", "value": "application/json"}],
            "url": "{{baseUrl}}" + url,
            "description": description,
            "body": {"mode": "raw", "raw": json.dumps(body, ensure_ascii=False, indent=2)},
        },
        "response": [],
    }


def reason_tests(reasons: list[str], status: list[str] | None = None) -> list[str]:
    tests = [
        "pm.test('Status 200', function () { pm.response.to.have.status(200); });",
        f"pm.test('reason {' | '.join(reasons)}', function () {{",
        f"  pm.expect({json.dumps(reasons)}).to.include(pm.response.json().reason);",
        "});",
    ]
    if status:
        tests += [
            f"pm.test('status {' | '.join(status)}', function () {{",
            f"  pm.expect({json.dumps(status)}).to.include(pm.response.json().status);",
            "});",
        ]
    return tests + NO_CODES


CONS = "/api/v1/consultations"
INTERP = "/api/v1/interpretations"
items = [
    request(
        "activity_missing — quiero abrir un negocio",
        CONS,
        {"query": "quiero abrir un negocio"},
        "Sin actividad: reason activity_missing, missing_fields incluye activity.",
        reason_tests(["activity_missing"], ["needs_clarification"])
        + [
            "pm.test('interpretacion parcial', function () {",
            "  pm.expect(pm.response.json().interpretation.missing_fields).to.include('activity');",
            "});",
        ],
    ),
    request(
        "activity_not_in_catalog — tienda de regalos (candidatos)",
        CONS,
        {"query": "quiero abrir una tienda de regalos en Florida 500"},
        "Actividad fuera del catálogo: hasta 3 activity_candidates (sin LLM, por parecido de texto). "
        "El Frontend muestra las opciones y manda activity_code + address de vuelta.",
        reason_tests(["activity_not_in_catalog"], ["activity_unknown"])
        + [
            "pm.test('candidatos con rubro_16', function () {",
            "  var c = pm.response.json().interpretation.activity_candidates;",
            "  pm.expect(c.length).to.be.within(1, 3);",
            "  pm.expect(c.map(function (x) { return x.code; })).to.include('rubro_16');",
            "  pm.expect(pm.response.json().interpretation.location.address).to.eql('Florida 500');",
            "});",
        ],
    ),
    request(
        "activity elegida — rubro_16 + Florida 500",
        CONS,
        {"activity_code": "rubro_16", "address": "Florida 500"},
        "Segundo paso del caso anterior: con el candidato elegido la consulta sigue.",
        [
            "pm.test('Status 200', function () { pm.response.to.have.status(200); });",
            "pm.test('sigue sin reason de actividad', function () {",
            "  var j = pm.response.json();",
            "  pm.expect(j.interpretation.activity.normalized_category).to.eql('rubro_16');",
            "  pm.expect(['activity_missing', 'activity_not_in_catalog']).to.not.include(j.reason);",
            "});",
        ],
    ),
    request(
        "location_missing — cafeteria sin direccion",
        CONS,
        {"query": "quiero abrir una cafeteria"},
        "Rubro sin dirección ni barrio.",
        reason_tests(["location_missing"], ["needs_clarification"])
        + [
            "pm.test('rubro ya detectado', function () {",
            "  pm.expect(pm.response.json().interpretation.activity.normalized_category).to.eql('rubro_102');",
            "});",
        ],
    ),
    request(
        "location_neighborhood_only — peluqueria en Belgrano",
        CONS,
        {"query": "Peluquería en Belgrano"},
        "Rubro + barrio sin calle: partial con trámites y la sede de la Comuna 13, sin zonificación.",
        reason_tests(["location_neighborhood_only"], ["partial"])
        + [
            "pm.test('sede de la comuna 13', function () {",
            "  var j = pm.response.json();",
            "  pm.expect(j.location.status).to.eql('neighborhood');",
            "  pm.expect(j.location.commune).to.eql('13');",
            "  pm.expect(j.zoning).to.eql(null);",
            "  pm.expect(j.physical_offices.some(function (o) { return o.commune === '13'; })).to.be.true;",
            "});",
        ],
    ),
    request(
        "location_not_found — calle inexistente",
        CONS,
        {"activity_code": "rubro_102", "address": "Calle Inexistente 123"},
        "El geocodificador no encuentra la dirección.",
        reason_tests(["location_not_found"], ["location_not_found"]),
    ),
    request(
        "location_ambiguous — Palermo",
        CONS,
        {"activity_code": "rubro_102", "address": "Palermo"},
        "Con el geocodificador simulado 'Palermo' es ambiguo; con USIG suele dar location_not_found.",
        reason_tests(["location_ambiguous", "location_not_found"]),
    ),
    request(
        "location_outside_caba — Mar del Plata",
        CONS,
        {"activity_code": "rubro_102", "address": "Mar del Plata"},
        "Fuera de CABA (con USIG puede dar location_not_found).",
        reason_tests(["location_outside_caba", "location_not_found"]),
    ),
    request(
        "topic_out_of_scope — como saco el DNI",
        CONS,
        {"query": "cómo saco el DNI"},
        "La consulta no es sobre abrir una actividad.",
        reason_tests(["topic_out_of_scope"], ["out_of_scope"]),
    ),
    request(
        "Interpret — barrio y candidatos",
        INTERP,
        {"query": "quiero poner una barbería en Belgrano"},
        "La interpretación trae neighborhood_id, commune y missing_fields=['address'].",
        [
            "pm.test('Status 200', function () { pm.response.to.have.status(200); });",
            "pm.test('barrio belgrano', function () {",
            "  var j = pm.response.json();",
            "  pm.expect(j.location.neighborhood_id).to.eql('belgrano');",
            "  pm.expect(j.location.commune).to.eql('13');",
            "  pm.expect(j.missing_fields).to.eql(['address']);",
            "  pm.expect(j.reason).to.eql('location_neighborhood_only');",
            "  pm.expect(j).to.not.have.property('clarification_question');",
            "});",
        ],
    ),
]

folder = next((f for f in data["item"] if f["name"] == FOLDER), None)
if folder is None:
    folder = {"name": FOLDER, "item": []}
    names = [f["name"] for f in data["item"]]
    data["item"].insert(names.index("04 Interpretations") + 1 if "04 Interpretations" in names else len(names), folder)
folder["description"] = "Un caso por cada reason del contrato de aclaraciones (documents/endpoints.md)."
folder["item"] = items

# Requests that changed with the new contract.
for f in data["item"]:
    for item in f.get("item", []):
        if item["name"] == "POST Interpret — actividad fuera de catalogo":
            item["event"] = [
                {
                    "listen": "test",
                    "script": {
                        "type": "text/javascript",
                        "exec": [
                            "pm.test('Status 200', function () { pm.response.to.have.status(200); });",
                            "pm.test('reason fijo', function () {",
                            "  pm.expect(pm.response.json()).to.have.property('reason');",
                            "  pm.expect(pm.response.json()).to.not.have.property('clarification_question');",
                            "});",
                        ],
                    },
                }
            ]

p.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("OK")
