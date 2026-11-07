"""Demonstração 1 — Workshop (Oficina).

A classe abaixo é a aplicação inteira: implementa só os dois hotspots do
``EventFramework``. Validação, ordem dos passos e construção do evento vêm do
framework. O backend é compartilhado com o Hackathon, mas a página é própria
desta aplicação (``demonstracoes/workshop/pagina.py``).
"""
import os
from pathlib import Path
from typing import Any

from framework.base import EventFramework

from demonstracoes.comum.servidor import create_demo_app
from demonstracoes.workshop.pagina import render

PORTA = 8101
LIMITE_NOME = 60
BANCO = Path(
    os.environ.get("CONFERA_WORKSHOP_DB", Path(__file__).with_name("workshop.db"))
)


class Workshop(EventFramework):
    """Oficina: reutiliza o framework e limita o tamanho do nome."""

    # HOTSPOT 1 (obrigatório): identidade do evento.
    def configure(self, data: dict[str, Any]) -> dict[str, Any]:
        configurado = dict(data)
        configurado["category"] = "Oficina"
        return configurado

    # HOTSPOT 2 (hook opcional): regra própria da aplicação.
    def check_rules(self, data: dict[str, Any]) -> None:
        if len(str(data["name"])) > LIMITE_NOME:
            raise ValueError(
                f"O nome da oficina deve ter no máximo {LIMITE_NOME} caracteres."
            )


app = create_demo_app(
    titulo="Workshop",
    aplicacao=Workshop,
    com_inscricoes=True,
    pagina=render,
    caminho_banco=BANCO,
)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=PORTA)
