from abc import ABC, abstractmethod
from typing import Any

class EventInterface(ABC):
    @abstractmethod
    def create(self, data: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError

class ParticipantInterface(ABC):
    @abstractmethod
    def validate(self, data: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError

class RegistrationInterface(ABC):
    @abstractmethod
    def validate(self, data: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError
