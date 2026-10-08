"""Fix Postman collection URLs and add interpretations folder."""

from __future__ import annotations

import json
from pathlib import Path

p = Path("postman/InobaLab-TECBA.postman_collection.json")
data = json.loads(p.read_text(encoding="utf-8"))


def walk(items: list) -> None:
    for item in items:
        if "item" in item:
            walk(item["item"])
        req = item.get("request")
        if not req:
            continue
        url = req.get("url")
        if isinstance(url, dict) and url.get("raw"):
            req["url"] = url["raw"]


walk(data["item"])

names = [i["name"] for i in data["item"]]
if "04 Interpretations" not in names:
    data["item"].append(
        {
            "name": "04 Interpretations",
            "item": [
                {
                    "name": "POST Interpret — cafeteria Corrientes",
                    "event": [
                        {
                            "listen": "test",
                            "script": {
                                "type": "text/javascript",
                                "exec": [
                                    "pm.test('Status 200', function () { pm.response.to.have.status(200); });",
                                    "pm.test('Ready for geocoding', function () {",
                                    "  var j = pm.response.json();",
                                    "  pm.expect(j.status).to.eql('ready_for_geocoding');",
                                    "  pm.expect(j.activity.normalized_category).to.eql('rubro_102');",
                                    "  pm.expect(j.location.address).to.be.ok;",
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
                                    "query": "Quiero abrir una cafeteria en Av. Corrientes 2500. Que tengo que hacer?",
                                    "conversation_id": None,
                                },
                                ensure_ascii=False,
                                indent=2,
                            ),
                        },
                        "url": "{{baseUrl}}/api/v1/interpretations",
                        "description": "Etapa 4 — extrae cafe + direccion. Sin LLM_API_KEY usa mock.",
                    },
                    "response": [],
                },
                {
                    "name": "POST Interpret — local de ropa",
                    "request": {
                        "method": "POST",
                        "header": [{"key": "Content-Type", "value": "application/json"}],
                        "body": {
                            "mode": "raw",
                            "raw": json.dumps(
                                {
                                    "query": "Quiero abrir un local de ropa en Av. del Libertador 1954"
                                },
                                ensure_ascii=False,
                                indent=2,
                            ),
                        },
                        "url": "{{baseUrl}}/api/v1/interpretations",
                    },
                    "response": [],
                },
                {
                    "name": "POST Interpret — sin direccion",
                    "event": [
                        {
                            "listen": "test",
                            "script": {
                                "type": "text/javascript",
                                "exec": [
                                    "pm.test('Needs clarification', function () {",
                                    "  pm.expect(pm.response.json().status).to.eql('needs_clarification');",
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
                                {"query": "Quiero abrir una cafeteria"},
                                ensure_ascii=False,
                                indent=2,
                            ),
                        },
                        "url": "{{baseUrl}}/api/v1/interpretations",
                    },
                    "response": [],
                },
                {
                    "name": "POST Interpret — actividad fuera de catalogo",
                    "request": {
                        "method": "POST",
                        "header": [{"key": "Content-Type", "value": "application/json"}],
                        "body": {
                            "mode": "raw",
                            "raw": json.dumps(
                                {
                                    "query": "Quiero abrir una veterinaria en Av. Corrientes 2500"
                                },
                                ensure_ascii=False,
                                indent=2,
                            ),
                        },
                        "url": "{{baseUrl}}/api/v1/interpretations",
                    },
                    "response": [],
                },
            ],
        }
    )

p.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("OK", [i["name"] for i in data["item"]])
