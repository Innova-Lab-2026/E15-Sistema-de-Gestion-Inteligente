"""Update Postman tests for curated tramites."""

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
    if "GET Sources (tramites curados)" not in names:
        catalog["item"].append(
            {
                "name": "GET Sources (tramites curados)",
                "event": [
                    {
                        "listen": "test",
                        "script": {
                            "type": "text/javascript",
                            "exec": [
                                "pm.test('Has curated procedure sources', function () {",
                                "  var items = pm.response.json();",
                                "  var ids = items.map(i => i.id);",
                                "  pm.expect(ids).to.include('source-001');",
                                "  pm.expect(ids).to.include('source-005');",
                                "  pm.expect(ids).to.include('source-006');",
                                "  var guia = items.find(i => i.id === 'source-001');",
                                "  pm.expect(guia.url).to.include('como-habilitar-tu-local-comercial');",
                                "});",
                            ],
                        },
                    }
                ],
                "request": {
                    "method": "GET",
                    "header": [],
                    "url": "{{baseUrl}}/api/v1/sources",
                    "description": "Etapa 3b — fuentes de tramites curados con URL oficial.",
                },
                "response": [],
            }
        )

consult = find_folder("03 Consultations")
if consult is not None:
    for item in consult["item"]:
        if item["name"] == "POST Consultation — cafeteria + Corrientes (deterministic)":
            item["event"][0]["script"]["exec"] = [
                "pm.test('Status 200', function () { pm.response.to.have.status(200); });",
                "pm.test('Curated tramites + zoning', function () {",
                "  var j = pm.response.json();",
                "  pm.expect(['complete','partial']).to.include(j.status);",
                "  pm.expect(j.location.status).to.eql('confirmed');",
                "  pm.expect(j.requirements.length).to.be.above(0);",
                "  pm.expect(j.requirements[0].steps.length).to.eql(6);",
                "  pm.expect(j.requirements[0].description).to.include('buenosaires.gob.ar');",
                "  pm.expect(j.steps[0].url_fuente).to.be.ok;",
                "  pm.expect(j.zoning).to.be.ok;",
                "  pm.expect(j.zoning.parcel.smp).to.be.ok;",
                "  var sourceIds = j.sources.map(s => s.id);",
                "  pm.expect(sourceIds).to.include('source-005');",
                "});",
            ]
            break

p.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("OK")
