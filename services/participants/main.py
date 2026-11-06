import sqlite3
from pathlib import Path
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from framework.components import ParticipantComponent

DB = Path(__file__).with_name("participants.db")
app = FastAPI(title="Confera - Participant Service", version="1.0.0")
component = ParticipantComponent()

class ParticipantInput(BaseModel):
    name: str
    email: str

def connect():
    db = sqlite3.connect(DB)
    db.row_factory = sqlite3.Row
    return db

def init_db():
    with connect() as db:
        db.execute("""CREATE TABLE IF NOT EXISTS participants (
            id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, email TEXT NOT NULL UNIQUE)""")

init_db()

@app.get("/health")
def health():
    return {"service":"participants","status":"ok"}

@app.post("/participants", status_code=201)
def create_participant(payload: ParticipantInput):
    try:
        data = component.validate(payload.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=400,detail=str(exc)) from exc
    try:
        with connect() as db:
            cursor = db.execute("INSERT INTO participants(name,email) VALUES(?,?)",(data["name"],data["email"]))
            participant_id = cursor.lastrowid
    except sqlite3.IntegrityError as exc:
        raise HTTPException(status_code=409,detail="Este e-mail já está cadastrado.") from exc
    return {"id":participant_id,**data}

@app.get("/participants")
def list_participants():
    with connect() as db:
        rows = db.execute("SELECT * FROM participants ORDER BY name").fetchall()
    return [dict(row) for row in rows]

@app.get("/participants/{participant_id}")
def get_participant(participant_id: int):
    with connect() as db:
        row = db.execute("SELECT * FROM participants WHERE id=?",(participant_id,)).fetchone()
    if row is None:
        raise HTTPException(status_code=404,detail="Participante não encontrado.")
    return dict(row)

@app.put("/participants/{participant_id}")
def update_participant(participant_id: int, payload: ParticipantInput):
    try:
        data = component.validate(payload.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=400,detail=str(exc)) from exc
    try:
        with connect() as db:
            cursor = db.execute("UPDATE participants SET name=?,email=? WHERE id=?",
                (data["name"],data["email"],participant_id))
    except sqlite3.IntegrityError as exc:
        raise HTTPException(status_code=409,detail="Este e-mail já está cadastrado.") from exc
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404,detail="Participante não encontrado.")
    return {"id":participant_id,**data}

@app.delete("/participants/{participant_id}")
def delete_participant(participant_id: int):
    with connect() as db:
        cursor = db.execute("DELETE FROM participants WHERE id=?",(participant_id,))
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404,detail="Participante não encontrado.")
    return {"message":"Participante removido."}
