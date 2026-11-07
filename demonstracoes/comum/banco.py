"""Persistência SQLite das demonstrações.

Cada aplicação usa seu próprio arquivo de banco, como os microsserviços do
projeto. A aplicação sem inscrições cria apenas a tabela de eventos.
"""
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator


@contextmanager
def abrir(caminho: str | Path) -> Iterator[sqlite3.Connection]:
    """Abre uma conexão, confirma no sucesso e desfaz em caso de erro."""
    conexao = sqlite3.connect(caminho)
    conexao.row_factory = sqlite3.Row
    try:
        yield conexao
    except Exception:
        conexao.rollback()
        raise
    else:
        conexao.commit()
    finally:
        conexao.close()


def inicializar(caminho: str | Path, com_inscricoes: bool) -> None:
    """Cria o arquivo e as tabelas necessárias, se ainda não existirem."""
    caminho = Path(caminho)
    caminho.parent.mkdir(parents=True, exist_ok=True)

    with abrir(caminho) as db:
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS eventos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT NOT NULL DEFAULT '',
                date TEXT NOT NULL,
                location TEXT NOT NULL,
                category TEXT NOT NULL
            )
            """
        )
        if com_inscricoes:
            db.execute(
                """
                CREATE TABLE IF NOT EXISTS participantes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT NOT NULL COLLATE NOCASE UNIQUE
                )
                """
            )
            db.execute(
                """
                CREATE TABLE IF NOT EXISTS inscricoes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_id INTEGER NOT NULL,
                    participant_id INTEGER NOT NULL,
                    status TEXT NOT NULL DEFAULT 'active'
                )
                """
            )


def linha(registro: sqlite3.Row | None) -> dict | None:
    """Converte uma linha do SQLite em dicionário."""
    return dict(registro) if registro is not None else None


def linhas(registros: list[sqlite3.Row]) -> list[dict]:
    """Converte várias linhas do SQLite em dicionários."""
    return [dict(registro) for registro in registros]
