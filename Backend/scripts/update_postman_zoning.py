"""Add epok zoning requests to Postman collection."""

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


loc = find_folder("02 Location")
assert loc is not None
names = [i["name"] for i in loc["item"]]
if "POST Zoning — Corrientes coords + rubro_102" not in names:
    loc["item"].append(
        {
            "name": "POST Zoning — Corrientes coords + rubro_102",
            "event": [
                {
                    "listen": "test",
                    "script": {
                        "type": "text/javascript",
                        "exec": [
                            "pm.test('Status 200', function () { pm.response.to.have.status(200); });",
                            "pm.test('Has smp and mixtura', function () {",
                            "  var j = pm.response.json();",
                            "  pm.expect(['ok','rubro_allowed','rubro_not_allowed']).to.include(j.status);",
                            "  pm.expect(j.parcel).to.be.ok;",
                            "  pm.expect(j.parcel.smp).to.be.ok;",
                            "  pm.expect(j.mixtura).to.be.a('number');",
                            "  pm.expect(j.epok_rubro_id).to.eql(102);",
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
                            "latitude": -34.604,
                            "longitude": -58.413,
                            "activity_code": "rubro_102",
                        },
                        ensure_ascii=False,
                        indent=2,
                    ),
                },
                "url": "{{baseUrl}}/api/v1/locations/zoning",
                "description": "Etapa 3b — parcela/smp + mixtura + check rubro gastronomia.",
            },
            "response": [],
        }
    )

consult = find_folder("03 Consultations")
assert consult is not None
# enrich first consultation test
for item in consult["item"]:
    if item["name"] == "POST Consultation — cafeteria + Corrientes (deterministic)":
        item["event"][0]["script"]["exec"] = [
            "pm.test('Status 200', function () { pm.response.to.have.status(200); });",
            "pm.test('Complete with requirements and zoning', function () {",
            "  var j = pm.response.json();",
            "  pm.expect(['complete','partial']).to.include(j.status);",
            "  pm.expect(j.location.status).to.eql('confirmed');",
            "  pm.expect(j.requirements.length).to.be.above(0);",
            "  pm.expect(j.sources.length).to.be.above(0);",
            "  pm.expect(j.zoning).to.be.ok;",
            "  pm.expect(j.zoning.parcel.smp).to.be.ok;",
            "});",
        ]
        item["request"]["description"] = (
            "Etapa 3+3b — deterministico con zoning epok (smp/mixtura/rubro)."
        )
        break

p.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("OK")
