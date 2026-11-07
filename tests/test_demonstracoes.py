"""Testes das demonstrações de reúso (Workshop com inscrições, Hackathon sem)."""
import atexit
import os
import shutil
import tempfile
import unittest
from pathlib import Path

# Bancos temporários: os testes nunca tocam nos arquivos reais das demos.
DIRETORIO_BANCOS = tempfile.mkdtemp(prefix="confera-demos-")
atexit.register(shutil.rmtree, DIRETORIO_BANCOS, ignore_errors=True)
os.environ["CONFERA_WORKSHOP_DB"] = os.path.join(DIRETORIO_BANCOS, "workshop.db")
os.environ["CONFERA_HACKATHON_DB"] = os.path.join(DIRETORIO_BANCOS, "hackathon.db")

from fastapi.testclient import TestClient

from demonstracoes.comum.servidor import create_demo_app
from demonstracoes.hackathon.main import Hackathon
from demonstracoes.hackathon.main import app as hackathon_app
from demonstracoes.workshop.main import Workshop
from demonstracoes.workshop.main import app as workshop_app

BASE = {
    "name": "Evento de teste",
    "description": "Descrição com mais de quarenta caracteres para o hackathon.",
    "date": "2026-12-10",
    "location": "UFAL",
}


class WorkshopTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(workshop_app)

    def _email(self):
        return f"ana.{self._testMethodName}@example.com"

    def test_page_is_user_facing(self):
        page = self.client.get("/").text
        self.assertIn("Oficina", page)
        self.assertIn("Nova oficina", page)
        self.assertIn("Oficinas", page)
        self.assertNotIn("EventFramework", page)
        self.assertNotIn("sobre esta página", page.lower())

    def test_page_shows_enrollment_areas(self):
        page = self.client.get("/").text
        self.assertIn("Quem vai participar", page)
        self.assertIn("Inscrições", page)
        self.assertIn('id="participant-form"', page)
        self.assertIn('id="registration-form"', page)
        self.assertNotIn("ParticipantComponent", page)
        self.assertNotIn("RegistrationComponent", page)

    def test_create_uses_inherited_template_and_hotspot(self):
        r = self.client.post("/api/eventos", json={**BASE, "name": "Oficina de Python"})
        self.assertEqual((r.status_code, r.json()["category"]), (201, "Oficina"))

    def test_own_rule_rejects_long_name(self):
        r = self.client.post("/api/eventos", json={**BASE, "name": "x" * 61})
        self.assertEqual(r.status_code, 400)
        self.assertIn("60 caracteres", r.json()["detail"])

    def test_inherited_validation_rejects_empty_payload(self):
        r = self.client.post("/api/eventos", json={})
        self.assertEqual(r.status_code, 400)
        self.assertIn("Campos obrigatórios ausentes", r.json()["detail"])

    def test_participant_email_validation(self):
        r = self.client.post(
            "/api/participantes", json={"name": "Ana", "email": "invalido"}
        )
        self.assertEqual(r.status_code, 400)

    def test_participant_duplicate_email(self):
        email = self._email()
        first = self.client.post("/api/participantes", json={"name": "Ana", "email": email})
        second = self.client.post("/api/participantes", json={"name": "Ana", "email": email})
        self.assertEqual(first.status_code, 201)
        self.assertEqual(second.status_code, 409)

    def test_participant_duplicate_email_is_case_insensitive(self):
        email = self._email()
        first = self.client.post("/api/participantes", json={"name": "Ana", "email": email})
        second = self.client.post(
            "/api/participantes", json={"name": "Ana", "email": email.upper()}
        )
        self.assertEqual(first.status_code, 201)
        self.assertEqual(second.status_code, 409)

    def test_enrollment_flow(self):
        evento = self.client.post(
            "/api/eventos", json={**BASE, "name": "Oficina com inscrição"}
        ).json()
        participante = self.client.post(
            "/api/participantes", json={"name": "Ana", "email": self._email()}
        ).json()

        inscricao = self.client.post(
            "/api/inscricoes",
            json={"event_id": evento["id"], "participant_id": participante["id"]},
        )
        self.assertEqual(inscricao.status_code, 201)
        self.assertEqual(inscricao.json()["status"], "active")

        duplicada = self.client.post(
            "/api/inscricoes",
            json={"event_id": evento["id"], "participant_id": participante["id"]},
        )
        self.assertEqual(duplicada.status_code, 409)

        cancelada = self.client.patch(
            f"/api/inscricoes/{inscricao.json()['id']}/cancelar"
        )
        self.assertEqual(cancelada.json()["status"], "cancelled")

    def test_registration_requires_existing_event(self):
        participante = self.client.post(
            "/api/participantes", json={"name": "Ana", "email": self._email()}
        ).json()
        r = self.client.post(
            "/api/inscricoes",
            json={"event_id": 999999, "participant_id": participante["id"]},
        )
        self.assertEqual(r.status_code, 404)

    def test_registration_requires_existing_participant(self):
        evento = self.client.post(
            "/api/eventos", json={**BASE, "name": "Oficina sem participante"}
        ).json()
        r = self.client.post(
            "/api/inscricoes",
            json={"event_id": evento["id"], "participant_id": 999999},
        )
        self.assertEqual(r.status_code, 404)


class HackathonTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(hackathon_app)

    def test_page_is_user_facing(self):
        page = self.client.get("/").text
        self.assertIn("hackathon", page)
        self.assertIn("Maratona de Programação", page)
        self.assertIn("criar evento", page)
        self.assertIn("eventos", page)
        self.assertNotIn("EventFramework", page)
        self.assertNotIn("inscri", page.lower())

    def test_enrollment_is_not_enabled(self):
        page = self.client.get("/").text
        self.assertNotIn('id="participant-form"', page)
        self.assertNotIn('id="registration-form"', page)
        self.assertEqual(self.client.get("/api/participantes").status_code, 404)
        self.assertEqual(self.client.get("/api/inscricoes").status_code, 404)

    def test_create_uses_inherited_template_and_hotspot(self):
        r = self.client.post("/api/eventos", json=BASE)
        self.assertEqual(
            (r.status_code, r.json()["category"]),
            (201, "Maratona de Programação"),
        )

    def test_own_rule_requires_description(self):
        r = self.client.post("/api/eventos", json={**BASE, "description": "curta"})
        self.assertEqual(r.status_code, 400)
        self.assertIn("40 caracteres", r.json()["detail"])


class SqlitePersistenceTests(unittest.TestCase):
    def _montar_workshop(self, banco: Path):
        return create_demo_app(
            titulo="Workshop",
            aplicacao=Workshop,
            com_inscricoes=True,
            pagina=lambda: "<!doctype html><title>teste</title>",
            caminho_banco=banco,
        )

    def test_workshop_data_survives_new_app_instance(self):
        with tempfile.TemporaryDirectory() as pasta:
            banco = Path(pasta) / "workshop.db"

            primeiro = TestClient(self._montar_workshop(banco))
            evento = primeiro.post(
                "/api/eventos", json={**BASE, "name": "Oficina persistida"}
            ).json()
            participante = primeiro.post(
                "/api/participantes",
                json={"name": "Ana", "email": "persistencia@example.com"},
            ).json()
            primeiro.post(
                "/api/inscricoes",
                json={
                    "event_id": evento["id"],
                    "participant_id": participante["id"],
                },
            )

            # Uma nova instância do app reabre o mesmo arquivo SQLite.
            segundo = TestClient(self._montar_workshop(banco))
            self.assertEqual(
                [e["id"] for e in segundo.get("/api/eventos").json()], [evento["id"]]
            )
            self.assertEqual(
                segundo.get("/api/participantes").json()[0]["email"],
                "persistencia@example.com",
            )
            self.assertEqual(
                segundo.get("/api/inscricoes").json()[0]["status"], "active"
            )
            self.assertTrue(banco.exists())



if __name__ == "__main__":
    unittest.main()
