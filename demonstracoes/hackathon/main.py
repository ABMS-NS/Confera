"""Demonstração 2 — Hackathon (Maratona de Programação).

Mesma estrutura do Workshop: só os hotspots mudam. O backend é compartilhado,
mas a página é própria desta aplicação (``demonstracoes/hackathon/pagina.py``)
e o serviço de inscrição não é habilitado.
"""
import os
from pathlib import Path
from typing import Any

from framework.base import EventFramework

from demonstracoes.comum.servidor import create_demo_app
from demonstracoes.hackathon.pagina import render

PORTA = 8102
MIN_DESCRICAO = 40
BANCO = Path(
    os.environ.get("CONFERA_HACKATHON_DB", Path(__file__).with_name("hackathon.db"))
)


class Hackathon(EventFramework):
    """Hackathon: reutiliza o framework e exige um tema/descrição."""

    # HOTSPOT 1 (obrigatório): identidade do evento.
    def configure(self, data: dict[str, Any]) -> dict[str, Any]:
        configurado = dict(data)
        configurado["category"] = "Maratona de Programação"
        return configurado

    # HOTSPOT 2 (hook opcional): regra própria da aplicação.
    def check_rules(self, data: dict[str, Any]) -> None:
        descricao = str(data.get("description", "")).strip()
        if len(descricao) < MIN_DESCRICAO:
            raise ValueError(
                "O Hackathon exige um tema (descrição) com pelo menos "
                f"{MIN_DESCRICAO} caracteres."
            )


app = create_demo_app(
    titulo="Hackathon",
    aplicacao=Hackathon,
    com_inscricoes=False,
    pagina=render,
    caminho_banco=BANCO,
)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=PORTA)
