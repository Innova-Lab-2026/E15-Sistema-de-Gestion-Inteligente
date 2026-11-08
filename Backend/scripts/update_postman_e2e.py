"""Add "06 End to end" to the Postman collection (B24): provider status, stored consultations
and the ambiguous-address flow with confirmation.

Run from Backend/: python scripts/update_postman_e2e.py
"""

from __future__ import annotations

import json
from pathlib import Path

p = Path("postman/InobaLab-TECBA.postman_collection.json")
data = json.loads(p.read_text(encoding="utf-8"))
FOLDER = "06 End to end"


def request(name, method, url, description, tests, body=None, prerequest=None):
    req = {"method": method, "header": [], "url": "{{baseUrl}}" + url, "description": description}
    if body is not None:
        req["header"].append({"key": "Content-Type", "value": "application/json"})
        req["body"] = {"mode": "raw", "raw": json.dumps(body, ensure_ascii=False, indent=2)}
    events = [{"listen": "test", "script": {"type": "text/javascript", "exec": tests}}]
    if prerequest:
        events.append({"listen": "prerequest", "script": {"type": "text/javascript", "exec": prerequest}})
    return {"name": name, "event": events, "request": req, "response": []}


OK = "pm.test('Status 200', function () { pm.response.to.have.status(200); });"
items = [
    request(
        "GET Status — proveedores activos",
        "GET",
        "/status",
        "Qué proveedores están activos (LLM o reglas, USIG o simulado, epok) sin mostrar claves.",
        [
            OK,
            "pm.test('providers sin claves', function () {",
            "  var j = pm.response.json();",
            "  pm.expect(j.providers.llm.active).to.be.oneOf(['llm', 'rules']);",
            "  pm.expect(j.providers.geocoder.simulated).to.be.a('boolean');",
            "  pm.expect(j.providers.epok.simulated).to.be.a('boolean');",
            "  pm.expect(pm.response.text()).to.not.match(/api_key|Bearer/i);",
            "});",
        ],
    ),
    request(
        "POST Consultation — guarda el caso",
        "POST",
        "/api/v1/consultations",
        "Cada consulta queda guardada: el id se usa en el pedido siguiente.",
        [
            OK,
            "var j = pm.response.json();",
            "pm.collectionVariables.set('consultationId', j.consultation_id);",
            "pm.collectionVariables.set('consultationStatus', j.status);",
            "pm.test('tiene consultation_id', function () { pm.expect(j.consultation_id).to.match(/^consultation-/); });",
        ],
        body={"query": "Quiero abrir un local de ropa en Av. Corrientes 2500"},
    ),
    request(
        "GET Consultation by id — mismo caso",
        "GET",
        "/api/v1/consultations/{{consultationId}}",
        "Devuelve la misma respuesta que el POST anterior.",
        [
            OK,
            "pm.test('mismo caso', function () {",
            "  var j = pm.response.json();",
            "  pm.expect(j.consultation_id).to.eql(pm.collectionVariables.get('consultationId'));",
            "  pm.expect(j.status).to.eql(pm.collectionVariables.get('consultationStatus'));",
            "});",
        ],
    ),
    request(
        "GET Consultation by id — inexistente",
        "GET",
        "/api/v1/consultations/consultation-doesnotexist",
        "404 con el formato único de errores.",
        [
            "pm.test('Status 404', function () { pm.response.to.have.status(404); });",
            "pm.test('not_found', function () { pm.expect(pm.response.json().error.code).to.eql('not_found'); });",
        ],
    ),
    request(
        "POST Consultation — dirección ambigua",
        "POST",
        "/api/v1/consultations",
        "Con el geocodificador simulado 'Palermo' es ambiguo: pide confirmar y no da requisitos.",
        [
            OK,
            "var j = pm.response.json();",
            "if (j.status === 'needs_location_confirmation') {",
            "  pm.collectionVariables.set('candidate', JSON.stringify(j.location.candidates[0]));",
            "  pm.test('sin respuesta oficial hasta confirmar', function () {",
            "    pm.expect(j.reason).to.eql('location_ambiguous');",
            "    pm.expect(j.requirements).to.eql([]);",
            "  });",
            "}",
        ],
        body={"activity_code": "rubro_102", "address": "Palermo"},
    ),
    request(
        "POST Consultation — ubicación confirmada",
        "POST",
        "/api/v1/consultations",
        "Segundo paso: la persona eligió un candidato y se manda como confirmed_location.",
        [
            OK,
            "pm.test('sigue con la ubicación confirmada', function () {",
            "  var j = pm.response.json();",
            "  pm.expect(['complete', 'partial']).to.include(j.status);",
            "  pm.expect(j.location.status).to.eql('confirmed');",
            "});",
        ],
        body={"activity_code": "rubro_102", "confirmed_location": "{{confirmedLocation}}"},
        prerequest=[
            "var c = JSON.parse(pm.collectionVariables.get('candidate') || 'null') || {",
            "  normalized_address: 'Av. Santa Fe y Coronel Diaz, Palermo, CABA', latitude: -34.5865, longitude: -58.4095,",
            "  commune: '14', neighborhood: 'Palermo' };",
            "pm.collectionVariables.set('confirmedLocation', JSON.stringify({",
            "  normalized_address: c.normalized_address, latitude: c.latitude, longitude: c.longitude,",
            "  commune: c.commune, neighborhood: c.neighborhood }));",
        ],
    ),
]
# confirmed_location goes as raw JSON, not as a quoted string.
items[-1]["request"]["body"]["raw"] = (
    '{\n  "activity_code": "rubro_102",\n  "confirmed_location": {{confirmedLocation}}\n}'
)

folder = next((f for f in data["item"] if f["name"] == FOLDER), None)
if folder is None:
    folder = {"name": FOLDER, "item": []}
    names = [f["name"] for f in data["item"]]
    data["item"].insert(names.index("90 Errors & limits") if "90 Errors & limits" in names else len(names), folder)
folder["description"] = "Estado de proveedores, consultas guardadas y confirmación de una dirección ambigua."
folder["item"] = items

variables = {v["key"] for v in data.setdefault("variable", [])}
for key in ("consultationId", "consultationStatus", "candidate", "confirmedLocation"):
    if key not in variables:
        data["variable"].append({"key": key, "value": ""})

p.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("OK")
