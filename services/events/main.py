import sqlite3
from pathlib import Path
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from examples.secomp import Secomp
from examples.symposium import Symposium

DB = Path(__file__).with_name("events.db")
app = FastAPI(title="Confera - Event Service", version="1.0.0")

class EventInput(BaseModel):
    name: str
    description: str = ""
    date: str
    location: str
    application: str = "secomp"

def connect():
    db = sqlite3.connect(DB)
    db.row_factory = sqlite3.Row
    return db

def init_db():
    with connect() as db:
        db.execute("""CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL,
            description TEXT NOT NULL, date TEXT NOT NULL,
            location TEXT NOT NULL, category TEXT NOT NULL)""")

init_db()

@app.get("/health")
def health():
    return {"service":"events","status":"ok"}

@app.post("/events", status_code=201)
def create_event(payload: EventInput):
    data = payload.model_dump(exclude={"application"})
    framework = Symposium() if payload.application == "symposium" else Secomp()
    try:
        event = framework.create_event(data)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    with connect() as db:
        cursor = db.execute("INSERT INTO events(name,description,date,location,category) VALUES(?,?,?,?,?)",
            (event["name"],event["description"],event["date"],event["location"],event["category"]))
        event_id = cursor.lastrowid
    return {"id":event_id,**event}

@app.get("/events")
def list_events():
    with connect() as db:
        rows = db.execute("SELECT * FROM events ORDER BY date,id").fetchall()
    return [dict(row) for row in rows]

@app.get("/events/{event_id}")
def get_event(event_id: int):
    with connect() as db:
        row = db.execute("SELECT * FROM events WHERE id=?",(event_id,)).fetchone()
    if row is None:
        raise HTTPException(status_code=404,detail="Evento não encontrado.")
    return dict(row)

@app.put("/events/{event_id}")
def update_event(event_id: int, payload: EventInput):
    data = payload.model_dump(exclude={"application"})
    framework = Symposium() if payload.application == "symposium" else Secomp()
    try:
        event = framework.create_event(data)
    except ValueError as exc:
        raise HTTPException(status_code=400,detail=str(exc)) from exc
    with connect() as db:
        cursor = db.execute("UPDATE events SET name=?,description=?,date=?,location=?,category=? WHERE id=?",
            (event["name"],event["description"],event["date"],event["location"],event["category"],event_id))
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404,detail="Evento não encontrado.")
    return {"id":event_id,**event}

@app.delete("/events/{event_id}")
def delete_event(event_id: int):
    with connect() as db:
        cursor = db.execute("DELETE FROM events WHERE id=?",(event_id,))
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404,detail="Evento não encontrado.")
    return {"message":"Evento removido."}
