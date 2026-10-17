"""Add readiness and error-format requests to the Postman collection (hardening)."""

from __future__ import annotations

import json
from pathlib import Path

p = Path("postman/InobaLab-TECBA.postman_collection.json")
data = json.loads(p.read_text(encoding="utf-8"))

FOLDER = "90 Errors & limits"
ERROR_FORMAT_TEST = [
    "pm.test('Standard error format', function () {",
    "  var e = pm.response.json().error;",
    "  pm.expect(e).to.have.all.keys('code', 'message', 'detail', 'request_id');",
    "  pm.expect(e.request_id).to.eql(pm.response.headers.get('X-Request-ID'));",
    "});",
]


def find_folder(name: str):
    for item in data["item"]:
        if item["name"] == name:
            return item
    return None


def request(name, method, url, description, tests, body=None, headers=None):
    req = {
        "method": method,
        "header": list(headers or []),
        "url": "{{baseUrl}}" + url,
        "description": description,
    }
    if body is not None:
        req["header"].append({"key": "Content-Type", "value": "application/json"})
        req["body"] = {"mode": "raw", "raw": json.dumps(body, ensure_ascii=False, indent=2)}
    return {
        "name": name,
        "event": [{"listen": "test", "script": {"type": "text/javascript", "exec": tests}}],
        "request": req,
        "response": [],
    }


def status_and_code(status: int, code: str) -> list[str]:
    return [
        f"pm.test('Status {status}', function () {{ pm.response.to.have.status({status}); }});",
        *ERROR_FORMAT_TEST,
        f"pm.test('Code {code}', function () {{ pm.expect(pm.response.json().error.code).to.eql('{code}'); }});",
    ]


health = find_folder("00 Health")
assert health is not None
if "GET Ready" not in [i["name"] for i in health["item"]]:
    health["item"].append(
        request(
            "GET Ready",
            "GET",
            "/ready",
            "Readiness: DB + schema migrado. 503 database_unavailable si la base no responde.",
            [
                "pm.test('Status 200', function () { pm.response.to.have.status(200); });",
                "pm.test('Ready', function () { pm.expect(pm.response.json().status).to.eql('ready'); });",
            ],
        )
    )

location = find_folder("02 Location")
assert location is not None
for item in location["item"]:
    if item["name"] == "POST Geocode — empty address":
        item["event"][0]["script"]["exec"] = status_and_code(422, "invalid_request")

errors = find_folder(FOLDER)
if errors is None:
    errors = {"name": FOLDER, "item": []}
    data["item"].append(errors)
errors["item"] = [
    request(
        "POST Geocode — missing field",
        "POST",
        "/api/v1/locations/geocode",
        "Validacion: detail = [{field, message}] en espanol.",
        status_and_code(422, "invalid_request")
        + [
            "pm.test('Field detail', function () {",
            "  pm.expect(pm.response.json().error.detail[0].field).to.eql('address');",
            "});",
        ],
        body={},
    ),
    request(
        "POST Interpret — query too long",
        "POST",
        "/api/v1/interpretations",
        "Limite de largo: query <= 500 caracteres.",
        status_and_code(422, "invalid_request"),
        body={"query": "x" * 501},
    ),
    request(
        "POST Zoning — coordinates outside CABA",
        "POST",
        "/api/v1/locations/zoning",
        "Coordenadas acotadas a CABA.",
        status_and_code(422, "invalid_request"),
        body={"latitude": 0, "longitude": 0},
    ),
    request(
        "GET Unknown route",
        "GET",
        "/api/v1/does-not-exist",
        "Rutas inexistentes con el formato unico.",
        status_and_code(404, "not_found"),
    ),
    request(
        "GET Health — echoes X-Request-ID",
        "GET",
        "/health",
        "El X-Request-ID del cliente vuelve en la respuesta y en los logs.",
        [
            "pm.test('Echoes request id', function () {",
            "  pm.expect(pm.response.headers.get('X-Request-ID')).to.eql('postman-check-1');",
            "});",
        ],
        headers=[{"key": "X-Request-ID", "value": "postman-check-1"}],
    ),
]

p.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("OK")
