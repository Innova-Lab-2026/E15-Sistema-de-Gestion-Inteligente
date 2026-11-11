"""B19: /status says which providers are active, without showing keys."""

from __future__ import annotations


def test_status_with_simulated_providers(client):
    body = client.get("/status").json()
    assert body["status"] == "ok"
    providers = body["providers"]
    assert providers["geocoder"] == {"provider": "mock", "simulated": True, "breaker_open": False, "cached_addresses": 0}
    assert providers["epok"] == {"provider": "mock", "simulated": True}
    assert providers["llm"]["active"] == "rules"
    assert body["data"]["barrios"] == 48
    assert body["data"]["sinonimos"] > 0


def test_status_with_real_providers_never_shows_keys(client, override_settings):
    override_settings(
        geocoder_provider="usig",
        epok_provider="epok",
        llm_base_url="https://gemini.test/v1",
        llm_api_key="secret-main-key",
        llm_model="gemini-flash-lite-latest",
        llm_fallback_base_url="https://openrouter.test/api/v1",
        llm_fallback_api_key="secret-backup-key",
        llm_fallback_model="backup-model:free",
        debug=False,
    )
    response = client.get("/status")
    body = response.json()
    assert body["providers"]["geocoder"]["simulated"] is False
    assert body["providers"]["epok"]["simulated"] is False
    assert body["providers"]["llm"] == {
        "active": "llm",
        "model": "gemini-flash-lite-latest",
        "fallback": {"configured": True, "model": "backup-model:free"},
        "rules_header": False,
    }
    assert "secret" not in response.text
    assert "gemini.test" not in response.text and "openrouter.test" not in response.text
