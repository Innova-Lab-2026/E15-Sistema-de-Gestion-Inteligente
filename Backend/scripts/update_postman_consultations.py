"""Add Postman folder 03 Consultations."""

from __future__ import annotations

import json
from pathlib import Path

p = Path("postman/InobaLab-TECBA.postman_collection.json")
data = json.loads(p.read_text(encoding="utf-8"))

folder = {
    "name": "03 Consultations",
    "item": [
        {
            "name": "POST Consultation — cafeteria + Corrientes (deterministic)",
            "event": [
                {
                    "listen": "test",
                    "script": {
                        "type": "text/javascript",
                        "exec": [
                            "pm.test('Status 200', function () { pm.response.to.have.status(200); });",
                            "pm.test('Complete with requirements', function () {",
                            "  var j = pm.response.json();",
                            "  pm.expect(['complete','partial']).to.include(j.status);",
                            "  pm.expect(j.location.status).to.eql('confirmed');",
                            "  pm.expect(j.requirements.length).to.be.above(0);",
                            "  pm.expect(j.sources.length).to.be.above(0);",
                            "  pm.expect(j.requirements[0].source_ids.length).to.be.above(0);",
                            "});",
                        ],
                    },
                }
            ],
            "request": {
                "method": "POST",
                "header": [{"key": "Content-Type", "value": "application/json"}],
                "body": {
                    "mode": "raw",
                    "raw": json.dumps(
                        {
                            "activity_code": "rubro_102",
                            "address": "Av. Corrientes 2500",
                            "confirmed_location": None,
                        },
                        ensure_ascii=False,
                        indent=2,
                    ),
                },
                "url": "{{baseUrl}}/api/v1/consultations",
                "description": "Etapa 3 — camino feliz deterministico.",
            },
            "response": [],
        },
        {
            "name": "POST Consultation — NL query cafeteria",
            "event": [
                {
                    "listen": "test",
                    "script": {
                        "type": "text/javascript",
                        "exec": [
                            "pm.test('Status 200', function () { pm.response.to.have.status(200); });",
                            "pm.test('Interpreted cafeteria', function () {",
                            "  var j = pm.response.json();",
                            "  pm.expect(j.interpretation.activity.normalized_category).to.eql('rubro_102');",
                            "  pm.expect(j.location.status).to.eql('confirmed');",
                            "});",
                        ],
                    },
                }
            ],
            "request": {
                "method": "POST",
                "header": [{"key": "Content-Type", "value": "application/json"}],
                "body": {
                    "mode": "raw",
                    "raw": json.dumps(
                        {
                            "query": "Quiero abrir una cafeteria en Av. Corrientes 2500. Que tengo que hacer?"
                        },
                        ensure_ascii=False,
                        indent=2,
                    ),
                },
                "url": "{{baseUrl}}/api/v1/consultations",
                "description": "Etapa 3+4 — interpreta NL y completa orientacion.",
            },
            "response": [],
        },
        {
            "name": "POST Consultation — actividad invalida",
            "event": [
                {
                    "listen": "test",
                    "script": {
                        "type": "text/javascript",
                        "exec": [
                            "pm.test('activity_unknown', function () {",
                            "  pm.expect(pm.response.json().status).to.eql('activity_unknown');",
                            "});",
                        ],
                    },
                }
            ],
            "request": {
                "method": "POST",
                "header": [{"key": "Content-Type", "value": "application/json"}],
                "body": {
                    "mode": "raw",
                    "raw": json.dumps(
                        {
                            "activity_code": "veterinaria",
                            "address": "Av. Corrientes 2500",
                        },
                        ensure_ascii=False,
                        indent=2,
                    ),
                },
                "url": "{{baseUrl}}/api/v1/consultations",
            },
            "response": [],
        },
        {
            "name": "POST Consultation — fuera de CABA",
            "event": [
                {
                    "listen": "test",
                    "script": {
                        "type": "text/javascript",
                        "exec": [
                            "pm.test('out_of_scope or location_not_found', function () {",
                            "  pm.expect(['out_of_scope','location_not_found']).to.include(pm.response.json().status);",
                            "});",
                        ],
                    },
                }
            ],
            "request": {
                "method": "POST",
                "header": [{"key": "Content-Type", "value": "application/json"}],
                "body": {
                    "mode": "raw",
                    "raw": json.dumps(
                        {
                            "activity_code": "rubro_102",
                            "address": "Mar del Plata",
                        },
                        ensure_ascii=False,
                        indent=2,
                    ),
                },
                "url": "{{baseUrl}}/api/v1/consultations",
            },
            "response": [],
        },
    ],
}

# Insert after 02 Location if present
names = [i["name"] for i in data["item"]]
if "03 Consultations" in names:
    idx = names.index("03 Consultations")
    data["item"][idx] = folder
else:
    insert_at = len(data["item"])
    for i, name in enumerate(names):
        if name.startswith("04"):
            insert_at = i
            break
    data["item"].insert(insert_at, folder)

p.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("OK", [i["name"] for i in data["item"]])
