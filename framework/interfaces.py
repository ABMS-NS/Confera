"""Interfaces (contratos) dos componentes do framework.

Cada componente de software implementa uma destas interfaces. Quem usa o
componente conhece apenas o contrato, não a implementação.
"""
from abc import ABC, abstractmethod
from typing import Any


class EventInterface(ABC):
    @abstractmethod
    def create(self, data: dict[str, Any]) -> dict[str, Any]:
        """Recebe os dados de um evento e devolve o evento pronto (dict)."""
        raise NotImplementedError


class ParticipantInterface(ABC):
    @abstractmethod
    def validate(self, data: dict[str, Any]) -> dict[str, Any]:
        """Valida e normaliza nome e e-mail. Lança ValueError se inválido."""
        raise NotImplementedError


class RegistrationInterface(ABC):
    @abstractmethod
    def validate(self, data: dict[str, Any]) -> dict[str, Any]:
        """Valida e normaliza event_id e participant_id. Lança ValueError se inválido."""
        raise NotImplementedError
