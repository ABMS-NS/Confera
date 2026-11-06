import unittest
from examples.secomp import Secomp
from examples.symposium import Symposium
from framework.components import ParticipantComponent, RegistrationComponent

class EventFrameworkTests(unittest.TestCase):
    def setUp(self):
        self.data = {"name":"Evento de teste","description":"Descrição","date":"2026-11-20","location":"UFAL"}

    def test_secomp_category(self):
        self.assertEqual(Secomp().create_event(self.data)["category"], "Semana Acadêmica")

    def test_symposium_category(self):
        self.assertEqual(Symposium().create_event(self.data)["category"], "Simpósio Científico")

    def test_missing_required_field(self):
        with self.assertRaises(ValueError):
            Secomp().create_event({"name":"Evento"})

    def test_participant_email_validation(self):
        with self.assertRaises(ValueError):
            ParticipantComponent().validate({"name":"Ana","email":"invalido"})

    def test_registration_ids_are_normalized(self):
        self.assertEqual(RegistrationComponent().validate({"event_id":"2","participant_id":"7"}),
                         {"event_id":2,"participant_id":7})

if __name__ == "__main__":
    unittest.main()
