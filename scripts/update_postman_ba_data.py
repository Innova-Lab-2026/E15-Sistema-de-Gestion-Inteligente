"""Add BA Data open-data requests to Postman."""

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


folder = find_folder("01 Catalog")
assert folder is not None
names = [i["name"] for i in folder["item"]]
if "GET Open Data packages (BA Data)" not in names:
    folder["item"].append(
        {
            "name": "GET Open Data packages (BA Data)",
            "event": [
                {
                    "listen": "test",
                    "script": {
                        "type": "text/javascript",
                        "exec": [
                            "pm.test('Has BA Data packages', function () {",
                            "  var j = pm.response.json();",
                            "  pm.expect(j.packages.length).to.be.at.least(1);",
                            "  pm.expect(j.gastronomia.total).to.be.at.least(1000);",
                            "});",
                        ],
                    },
                }
            ],
            "request": {
                "method": "GET",
                "header": [],
                "url": "{{baseUrl}}/api/v1/open-data/packages",
                "description": "Etapa 3b — snapshot ETL BA Data.",
            },
            "response": [],
        }
    )
if "GET Gastronomy context Balvanera" not in names:
    folder["item"].append(
        {
            "name": "GET Gastronomy context Balvanera",
            "event": [
                {
                    "listen": "test",
                    "script": {
                        "type": "text/javascript",
                        "exec": [
                            "pm.test('Context for Balvanera/Comuna 3', function () {",
                            "  var j = pm.response.json();",
                            "  pm.expect(j.count_barrio).to.be.above(0);",
                            "  pm.expect(j.count_comuna).to.be.above(0);",
                            "});",
                        ],
                    },
                }
            ],
            "request": {
                "method": "GET",
                "header": [],
                "url": "{{baseUrl}}/api/v1/open-data/gastronomy-context?commune=3&neighborhood=Balvanera",
                "description": "Conteo BA Data por comuna/barrio.",
            },
            "response": [],
        }
    )

consult = find_folder("03 Consultations")
if consult is not None:
    for item in consult["item"]:
        if item["name"] == "POST Consultation — cafeteria + Corrientes (deterministic)":
            exec_lines = item["event"][0]["script"]["exec"]
            if not any("BA Data" in line for line in exec_lines):
                exec_lines[-2:-2] = [
                    "  var terr = (j.territorial_information || []).map(t => t.title).join('|');",
                    "  pm.expect(terr).to.include('BA Data');",
                ]
            break

p.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("OK")
