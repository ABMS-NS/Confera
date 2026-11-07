"""Testes de API (sem precisar subir os serviços): usam TestClient e banco temporário."""
import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from gateway import main as gateway_main
from services.events import main as events_main

BODY = {"name": "Evento", "description": "Descrição com mais de vinte caracteres",
        "date": "2026-11-20", "location": "UFAL", "application": "symposium"}


class EventServiceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        events_main.DB = Path(self.tmp.name) / "events.db"
        events_main.init_db()
        self.client = TestClient(events_main.app)

    def tearDown(self):
        self.tmp.cleanup()

    def test_create_uses_application_category(self):
        r = self.client.post("/events", json=BODY)
        self.assertEqual((r.status_code, r.json()["category"]), (201, "Simpósio Científico"))

    def test_symposium_rule_returns_400(self):
        r = self.client.post("/events", json={**BODY, "description": ""})
        self.assertEqual(r.status_code, 400)

    def test_unknown_application_returns_400(self):
        r = self.client.post("/events", json={**BODY, "application": "xyz"})
        self.assertEqual(r.status_code, 400)

    def test_update_keeps_chosen_application(self):  # regressão: antes voltava para SECOMP
        event_id = self.client.post("/events", json=BODY).json()["id"]
        r = self.client.put(f"/events/{event_id}", json={**BODY, "name": "Novo nome"})
        self.assertEqual(r.json()["category"], "Simpósio Científico")

    def test_application_is_required(self):
        body = {k: v for k, v in BODY.items() if k != "application"}
        self.assertEqual(self.client.post("/events", json=body).status_code, 422)


class GatewayTests(unittest.TestCase):
    def test_services_listing(self):
        data = TestClient(gateway_main.app).get("/services").json()
        self.assertEqual([s["port"] for s in data], [8000, 8001, 8002, 8003])
        self.assertEqual(data[0]["status"], "online")


if __name__ == "__main__":
    unittest.main()
