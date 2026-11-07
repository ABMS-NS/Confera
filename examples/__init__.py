"""Registro das aplicações construídas com o framework.

Para disponibilizar uma nova aplicação no sistema, basta importá-la e
adicioná-la ao dicionário APPLICATIONS.
"""
from framework.base import EventFramework

from .secomp import Secomp
from .symposium import Symposium

APPLICATIONS: dict[str, type[EventFramework]] = {
    "secomp": Secomp,
    "symposium": Symposium,
}


def get_application(key: str) -> EventFramework:
    """Instancia a aplicação pelo nome ou lança ValueError se não existir."""
    try:
        return APPLICATIONS[key]()
    except KeyError:
        raise ValueError(
            f"Aplicação desconhecida: '{key}'. Use: {', '.join(APPLICATIONS)}."
        ) from None
