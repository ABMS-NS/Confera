"""Aplicação 2: Simpósio Científico, construída reusando o framework."""
from typing import Any

from framework.base import EventFramework

MIN_DESCRIPTION = 20


class Symposium(EventFramework):
    # HOTSPOT 1: define a categoria do evento.
    def configure(self, data: dict[str, Any]) -> dict[str, Any]:
        configured = dict(data)
        configured["category"] = "Simpósio Científico"
        return configured

    # HOTSPOT 2: regra própria. Um simpósio precisa de um tema/resumo.
    def check_rules(self, data: dict[str, Any]) -> None:
        if len(str(data.get("description", "")).strip()) < MIN_DESCRIPTION:
            raise ValueError(
                f"O Simpósio exige uma descrição (tema) com pelo menos {MIN_DESCRIPTION} caracteres."
            )
