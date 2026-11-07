"""Fábrica de API compartilhada pelas demonstrações.

O backend (banco, dados e regras) é reutilizado pelas duas aplicações. A página
HTML é responsabilidade de cada aplicação: cada uma tem seu próprio
``pagina.py``, com layout, CSS e JavaScript próprios.

Cada demonstração recebe o caminho do seu arquivo SQLite. Sem inscrições, apenas
a tabela de eventos é criada e as rotas de participantes/inscrições não existem.
"""
import sqlite3
from pathlib import Path
from typing import Any, Callable

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from framework.base import EventFramework
from framework.components import ParticipantComponent, RegistrationComponent

from .banco import abrir, inicializar, linha, linhas

CAMPOS_EVENTO = "id, name, description, date, location, category"
CAMPOS_PARTICIPANTE = "id, name, email"
CAMPOS_INSCRICAO = "id, event_id, participant_id, status"


class EventoEntrada(BaseModel):
    """Entrada permissiva: a validação principal é a do framework."""

    name: str = ""
    description: str = ""
    date: str = ""
    location: str = ""


class ParticipanteEntrada(BaseModel):
    name: str = ""
    email: str = ""


class InscricaoEntrada(BaseModel):
    event_id: int | None = None
    participant_id: int | None = None


def create_demo_app(
    *,
    titulo: str,
    aplicacao: type[EventFramework],
    com_inscricoes: bool,
    pagina: Callable[[], str],
    caminho_banco: str | Path,
) -> FastAPI:
    """Monta a API de uma demonstração sobre um arquivo SQLite."""
    app = FastAPI(title=titulo)
    inicializar(caminho_banco, com_inscricoes)

    @app.get("/", response_class=HTMLResponse)
    def index() -> str:
        return pagina()

    @app.get("/health")
    def health() -> dict[str, Any]:
        return {"app": titulo, "status": "ok", "inscricoes": com_inscricoes}

    @app.get("/api/eventos")
    def listar_eventos() -> list[dict[str, Any]]:
        with abrir(caminho_banco) as db:
            return linhas(db.execute(f"SELECT {CAMPOS_EVENTO} FROM eventos ORDER BY id").fetchall())

    @app.post("/api/eventos", status_code=201)
    def criar_evento(payload: EventoEntrada) -> dict[str, Any]:
        try:
            # Chamada ao TEMPLATE METHOD herdado do framework.
            evento = aplicacao().create_event(payload.model_dump())
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

        with abrir(caminho_banco) as db:
            cursor = db.execute(
                """
                INSERT INTO eventos (name, description, date, location, category)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    evento["name"],
                    evento.get("description", ""),
                    evento["date"],
                    evento["location"],
                    evento["category"],
                ),
            )
            return linha(
                db.execute(
                    f"SELECT {CAMPOS_EVENTO} FROM eventos WHERE id = ?",
                    (cursor.lastrowid,),
                ).fetchone()
            )

    @app.delete("/api/eventos/{evento_id}")
    def remover_evento(evento_id: int) -> dict[str, str]:
        with abrir(caminho_banco) as db:
            cursor = db.execute("DELETE FROM eventos WHERE id = ?", (evento_id,))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Evento não encontrado.")
        return {"message": "Evento removido."}

    if com_inscricoes:

        @app.get("/api/participantes")
        def listar_participantes() -> list[dict[str, Any]]:
            with abrir(caminho_banco) as db:
                return linhas(
                    db.execute(
                        f"SELECT {CAMPOS_PARTICIPANTE} FROM participantes ORDER BY id"
                    ).fetchall()
                )

        @app.post("/api/participantes", status_code=201)
        def criar_participante(payload: ParticipanteEntrada) -> dict[str, Any]:
            try:
                dados = ParticipantComponent().validate(payload.model_dump())
            except ValueError as exc:
                raise HTTPException(status_code=400, detail=str(exc)) from exc

            try:
                with abrir(caminho_banco) as db:
                    cursor = db.execute(
                        "INSERT INTO participantes (name, email) VALUES (?, ?)",
                        (dados["name"], dados["email"]),
                    )
                    return linha(
                        db.execute(
                            f"SELECT {CAMPOS_PARTICIPANTE} FROM participantes WHERE id = ?",
                            (cursor.lastrowid,),
                        ).fetchone()
                    )
            except sqlite3.IntegrityError as exc:
                raise HTTPException(
                    status_code=409, detail="Este e-mail já está cadastrado."
                ) from exc

        @app.delete("/api/participantes/{participante_id}")
        def remover_participante(participante_id: int) -> dict[str, str]:
            with abrir(caminho_banco) as db:
                cursor = db.execute(
                    "DELETE FROM participantes WHERE id = ?", (participante_id,)
                )
            if cursor.rowcount == 0:
                raise HTTPException(
                    status_code=404, detail="Participante não encontrado."
                )
            return {"message": "Participante removido."}

        @app.get("/api/inscricoes")
        def listar_inscricoes() -> list[dict[str, Any]]:
            with abrir(caminho_banco) as db:
                return linhas(
                    db.execute(
                        f"SELECT {CAMPOS_INSCRICAO} FROM inscricoes ORDER BY id"
                    ).fetchall()
                )

        @app.post("/api/inscricoes", status_code=201)
        def criar_inscricao(payload: InscricaoEntrada) -> dict[str, Any]:
            try:
                dados = RegistrationComponent().validate(payload.model_dump())
            except ValueError as exc:
                raise HTTPException(status_code=400, detail=str(exc)) from exc

            with abrir(caminho_banco) as db:
                if db.execute(
                    "SELECT 1 FROM eventos WHERE id = ?", (dados["event_id"],)
                ).fetchone() is None:
                    raise HTTPException(status_code=404, detail="Evento não encontrado.")
                if db.execute(
                    "SELECT 1 FROM participantes WHERE id = ?",
                    (dados["participant_id"],),
                ).fetchone() is None:
                    raise HTTPException(
                        status_code=404, detail="Participante não encontrado."
                    )
                ativa = db.execute(
                    """
                    SELECT 1 FROM inscricoes
                    WHERE event_id = ? AND participant_id = ? AND status = 'active'
                    """,
                    (dados["event_id"], dados["participant_id"]),
                ).fetchone()
                if ativa is not None:
                    raise HTTPException(
                        status_code=409, detail="Participante já inscrito neste evento."
                    )

                cursor = db.execute(
                    """
                    INSERT INTO inscricoes (event_id, participant_id, status)
                    VALUES (?, ?, 'active')
                    """,
                    (dados["event_id"], dados["participant_id"]),
                )
                return linha(
                    db.execute(
                        f"SELECT {CAMPOS_INSCRICAO} FROM inscricoes WHERE id = ?",
                        (cursor.lastrowid,),
                    ).fetchone()
                )

        @app.patch("/api/inscricoes/{inscricao_id}/cancelar")
        def cancelar_inscricao(inscricao_id: int) -> dict[str, Any]:
            with abrir(caminho_banco) as db:
                registro = db.execute(
                    f"SELECT {CAMPOS_INSCRICAO} FROM inscricoes WHERE id = ?",
                    (inscricao_id,),
                ).fetchone()
                if registro is None:
                    raise HTTPException(
                        status_code=404, detail="Inscrição não encontrada."
                    )
                if registro["status"] == "active":
                    db.execute(
                        "UPDATE inscricoes SET status = 'cancelled' WHERE id = ?",
                        (inscricao_id,),
                    )
                    registro = db.execute(
                        f"SELECT {CAMPOS_INSCRICAO} FROM inscricoes WHERE id = ?",
                        (inscricao_id,),
                    ).fetchone()
                return linha(registro)

    return app
