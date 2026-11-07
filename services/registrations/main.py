"""Registration Service (porta 8003): inscrição de participantes em eventos.

Reusa o COMPONENTE RegistrationComponent (validação dos IDs) e CONSULTA os
outros dois serviços via HTTP antes de gravar. Banco próprio: registrations.db.
"""
import sqlite3
from pathlib import Path
import httpx
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from framework.components import RegistrationComponent

DB = Path(__file__).with_name("registrations.db")
EVENTS_URL = "http://127.0.0.1:8001"
PARTICIPANTS_URL = "http://127.0.0.1:8002"
app = FastAPI(title="Confera - Registration Service", version="1.0.0")
component = RegistrationComponent()

class RegistrationInput(BaseModel):
    event_id: int
    participant_id: int

def connect():
    db = sqlite3.connect(DB)
    db.row_factory = sqlite3.Row
    return db

def init_db():
    with connect() as db:
        db.execute("""CREATE TABLE IF NOT EXISTS registrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT, event_id INTEGER NOT NULL,
            participant_id INTEGER NOT NULL, status TEXT NOT NULL DEFAULT 'active')""")

init_db()

@app.get("/health")
def health():
    return {"service":"registrations","status":"ok"}

@app.post("/registrations", status_code=201)
async def create_registration(payload: RegistrationInput):
    try:
        data = component.validate(payload.model_dump())
    except ValueError as exc:  # antes isto virava HTTP 500
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    # Consulta os serviços dono dos dados: o evento e o participante existem?
    async with httpx.AsyncClient(timeout=5) as client:
        try:
            event = await client.get(f"{EVENTS_URL}/events/{data['event_id']}")
            participant = await client.get(f"{PARTICIPANTS_URL}/participants/{data['participant_id']}")
        except httpx.HTTPError as exc:
            raise HTTPException(status_code=503,detail="Não foi possível consultar os serviços relacionados.") from exc
    if event.status_code == 404:
        raise HTTPException(status_code=404,detail="Evento não encontrado.")
    if participant.status_code == 404:
        raise HTTPException(status_code=404,detail="Participante não encontrado.")
    if event.is_error or participant.is_error:
        raise HTTPException(status_code=503,detail="Falha ao consultar os serviços relacionados.")
    with connect() as db:
        duplicate = db.execute(
            "SELECT 1 FROM registrations WHERE event_id=? AND participant_id=? AND status='active'",
            (data["event_id"], data["participant_id"])).fetchone()
        if duplicate:
            raise HTTPException(status_code=409, detail="Participante já inscrito neste evento.")
        cursor = db.execute("INSERT INTO registrations(event_id,participant_id,status) VALUES(?,?,'active')",
            (data["event_id"],data["participant_id"]))
        registration_id = cursor.lastrowid
    return {"id":registration_id,**data,"status":"active"}

@app.get("/registrations")
def list_registrations(event_id: int | None = Query(default=None), status: str | None = Query(default=None)):
    if status not in (None,"active","cancelled"):
        raise HTTPException(status_code=400,detail="status deve ser active ou cancelled.")
    query, params = "SELECT * FROM registrations WHERE 1=1", []
    if event_id is not None:
        query += " AND event_id=?"
        params.append(event_id)
    if status is not None:
        query += " AND status=?"
        params.append(status)
    with connect() as db:
        rows = db.execute(query+" ORDER BY id",params).fetchall()
    return [dict(row) for row in rows]

@app.patch("/registrations/{registration_id}/cancel")
def cancel_registration(registration_id: int):
    with connect() as db:
        cursor = db.execute("UPDATE registrations SET status='cancelled' WHERE id=? AND status='active'",(registration_id,))
        row = db.execute("SELECT * FROM registrations WHERE id=?",(registration_id,)).fetchone()
    if row is None:
        raise HTTPException(status_code=404,detail="Inscrição não encontrada.")
    return dict(row)
