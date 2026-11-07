import unittest
from examples import APPLICATIONS, get_application
from examples.secomp import Secomp
from examples.symposium import Symposium
from framework.base import EventFramework
from framework.components import ParticipantComponent, RegistrationComponent

DATA = {"name": "Evento de teste", "description": "Descrição com mais de vinte caracteres",
        "date": "2026-11-20", "location": "UFAL"}


class EventFrameworkTests(unittest.TestCase):
    def test_secomp_category(self):
        self.assertEqual(Secomp().create_event(DATA)["category"], "Semana Acadêmica")

    def test_symposium_category(self):
        self.assertEqual(Symposium().create_event(DATA)["category"], "Simpósio Científico")

    def test_missing_required_field(self):  # frozen spot: vale para qualquer aplicação
        for app in (Secomp(), Symposium()):
            with self.assertRaises(ValueError):
                app.create_event({"name": "Evento"})

    def test_framework_is_abstract(self):
        with self.assertRaises(TypeError):
            EventFramework()

    def test_hook_default_allows_short_description(self):  # SECOMP herda o hook vazio
        self.assertEqual(Secomp().create_event({**DATA, "description": ""})["description"], "")

    def test_hook_overridden_by_symposium(self):  # Simpósio impõe regra própria
        with self.assertRaises(ValueError):
            Symposium().create_event({**DATA, "description": "curta"})

    def test_registry(self):
        self.assertEqual(set(APPLICATIONS), {"secomp", "symposium"})
        self.assertIsInstance(get_application("secomp"), Secomp)
        with self.assertRaises(ValueError):
            get_application("inexistente")

    def test_participant_email_validation(self):
        with self.assertRaises(ValueError):
            ParticipantComponent().validate({"name": "Ana", "email": "invalido"})

    def test_registration_ids_are_normalized(self):
        self.assertEqual(RegistrationComponent().validate({"event_id": "2", "participant_id": "7"}),
                         {"event_id": 2, "participant_id": 7})

    def test_registration_rejects_non_positive_ids(self):
        with self.assertRaises(ValueError):
            RegistrationComponent().validate({"event_id": -1, "participant_id": 1})


if __name__ == "__main__":
    unittest.main()
