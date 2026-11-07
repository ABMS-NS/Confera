"""Componentes reutilizáveis: implementam as interfaces do framework."""
from typing import Any
from .interfaces import EventInterface, ParticipantInterface, RegistrationInterface
from .models import Event

class EventComponent(EventInterface):
    """Monta o objeto Event a partir dos dados recebidos (remove espaços extras)."""

    def create(self, data: dict[str, Any]) -> dict[str, Any]:
        event = Event(
            name=data["name"].strip(),
            description=data.get("description", "").strip(),
            date=data["date"].strip(),
            location=data["location"].strip(),
            category=data["category"].strip(),
        )
        return event.to_dict()

class ParticipantComponent(ParticipantInterface):
    """Regra de participante: nome obrigatório e e-mail em formato válido."""

    def validate(self, data: dict[str, Any]) -> dict[str, Any]:
        name, email = str(data.get("name", "")).strip(), str(data.get("email", "")).strip()
        if not name:
            raise ValueError("O nome do participante é obrigatório.")
        if "@" not in email or "." not in email.split("@")[-1]:
            raise ValueError("Informe um e-mail válido.")
        return {"name": name, "email": email}

class RegistrationComponent(RegistrationInterface):
    """Regra de inscrição: os dois IDs devem ser inteiros positivos."""

    def validate(self, data: dict[str, Any]) -> dict[str, Any]:
        try:
            event_id, participant_id = int(data["event_id"]), int(data["participant_id"])
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError("event_id e participant_id devem ser números inteiros.") from exc
        if event_id <= 0 or participant_id <= 0:
            raise ValueError("Os identificadores devem ser positivos.")
        return {"event_id": event_id, "participant_id": participant_id}
