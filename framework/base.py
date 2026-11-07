"""Núcleo do framework Confera (padrão de projeto Template Method).

Tudo o que é igual para qualquer evento acadêmico fica AQUI (frozen spots).
Tudo o que muda de uma aplicação para outra fica nos HOTSPOTS, que cada
aplicação implementa em uma subclasse.
"""
from abc import ABC, abstractmethod
from typing import Any

from .components import EventComponent
from .interfaces import EventInterface


class EventFramework(ABC):
    """Classe abstrata de onde toda aplicação de eventos herda."""

    def __init__(self, component: EventInterface | None = None) -> None:
        # Componente reutilizável que monta o evento (composição / caixa-preta).
        self.event_component = component or EventComponent()

    # TEMPLATE METHOD -- FROZEN SPOT: a ordem dos passos é fixa e não deve
    # ser sobrescrita pelas subclasses.
    def create_event(self, data: dict[str, Any]) -> dict[str, Any]:
        """Algoritmo fixo: validar -> configurar -> aplicar regras -> construir."""
        self.validate(data)                              # 1. frozen spot
        configured = self.configure(data)                # 2. HOTSPOT obrigatório
        self.check_rules(configured)                     # 3. HOTSPOT opcional (hook)
        return self.event_component.create(configured)  # 4. frozen spot (componente)

    # FROZEN SPOT: validação comum a todas as aplicações.
    def validate(self, data: dict[str, Any]) -> None:
        required = ("name", "date", "location")
        missing = [f for f in required if not str(data.get(f, "")).strip()]
        if missing:
            raise ValueError("Campos obrigatórios ausentes: " + ", ".join(missing))

    # HOTSPOT 1 (abstrato): toda aplicação DEVE implementar.
    # Define a identidade do evento (ex.: a categoria).
    @abstractmethod
    def configure(self, data: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError

    # HOTSPOT 2 (hook): a aplicação PODE sobrescrever.
    # Por padrão não impõe nenhuma regra extra. Deve lançar ValueError se
    # os dados violarem uma regra da aplicação.
    def check_rules(self, data: dict[str, Any]) -> None:
        return None
