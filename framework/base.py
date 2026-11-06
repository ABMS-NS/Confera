from abc import ABC, abstractmethod
from typing import Any
from .components import EventComponent

class EventFramework(ABC):
    def __init__(self, component: EventComponent | None = None) -> None:
        self.event_component = component or EventComponent()

    def create_event(self, data: dict[str, Any]) -> dict[str, Any]:
        """Template Method: validar -> configurar -> construir evento."""
        self.validate(data)                    # frozen spot
        configured_data = self.configure(data) # hotspot
        return self.event_component.create(configured_data)

    def validate(self, data: dict[str, Any]) -> None:
        required = ("name", "date", "location")
        missing = [field for field in required if not str(data.get(field, "")).strip()]
        if missing:
            raise ValueError("Campos obrigatórios ausentes: " + ", ".join(missing))

    @abstractmethod
    def configure(self, data: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError
