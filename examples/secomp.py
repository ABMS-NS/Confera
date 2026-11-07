"""Aplicação 1: SECOMP (Semana Acadêmica), construída reusando o framework."""
from typing import Any

from framework.base import EventFramework


class Secomp(EventFramework):
    # HOTSPOT 1: define a categoria do evento.
    def configure(self, data: dict[str, Any]) -> dict[str, Any]:
        configured = dict(data)
        configured["category"] = "Semana Acadêmica"
        return configured

    # HOTSPOT 2 não foi sobrescrito: a SECOMP aceita qualquer descrição
    # (usa o comportamento padrão herdado do framework).
