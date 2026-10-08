"""Add Postman request for expanded catalog / ferreteria."""

from __future__ import annotations

import json
from pathlib import Path

p = Path("postman/InobaLab-TECBA.postman_collection.json")
data = json.loads(p.read_text(encoding="utf-8"))


def find_folder(name: str):
    for item in data["item"]:
        if item["name"] == name:
            return item
    return None


catalog = find_folder("01 Catalog")
if catalog is not None:
    names = [i["name"] for i in catalog["item"]]
    if "GET Activities (epok fields)" not in names:
        catalog["item"].insert(
            1,
            {
                "name": "GET Activities (epok fields)",
                "event": [
                    {
                        "listen": "test",
                        "script": {
                            "type": "text/javascript",
                            "exec": [
                                "pm.test('Has ferreteria rubro_309 and epok fields', function () {",
                                "  var items = pm.response.json();",
                                "  pm.expect(items.length).to.be.at.least(100);",
                                "  var hw = items.find(i => i.code === 'rubro_309');",
                                "  pm.expect(hw).to.be.ok;",
                                "  pm.expect(hw.epok_rubro_id).to.eql(309);",
                                "  pm.expect(hw.epok_category_id).to.eql(1);",
                                "});",
                            ],
                        },
                    }
                ],
                "request": {
                    "method": "GET",
                    "header": [],
                    "url": "{{baseUrl}}/api/v1/activities",
                    "description": "Catalogo medio alineado a epok.",
                },
                "response": [],
            },
        )

interp = find_folder("04 Interpretations")
if interp is not None:
    names = [i["name"] for i in interp["item"]]
    if "POST Interpret — ferreteria" not in names:
        interp["item"].insert(
            1,
            {
                "name": "POST Interpret — ferreteria",
                "event": [
                    {
                        "listen": "test",
                        "script": {
                            "type": "text/javascript",
                            "exec": [
                                "pm.test('ferreteria -> rubro_309', function () {",
                                "  var j = pm.response.json();",
                                "  pm.expect(j.status).to.eql('ready_for_geocoding');",
                                "  pm.expect(j.activity.normalized_category).to.eql('rubro_309');",
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
                                "query": "Quiero abrir una ferreteria en Santiago del Estero 112. Que tengo que hacer?"
                            },
                            ensure_ascii=False,
                            indent=2,
                        ),
                    },
                    "url": "{{baseUrl}}/api/v1/interpretations",
                },
                "response": [],
            },
        )

p.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("OK")
