"""API Gateway (porta 8000): ponto único de entrada do sistema.

Serve a interface web e encaminha (proxy) cada rota para o microsserviço
responsável. Também expõe GET /services com o status de cada serviço.
"""
import asyncio
from pathlib import Path

import httpx
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

EVENTS_URL = "http://127.0.0.1:8001"
PARTICIPANTS_URL = "http://127.0.0.1:8002"
REGISTRATIONS_URL = "http://127.0.0.1:8003"
# Catálogo dos microsserviços: nome, porta, responsabilidade e URL de health.
SERVICES = [
    {"name": "Event Service", "port": 8001, "role": "Eventos (usa o framework)", "url": EVENTS_URL},
    {"name": "Participant Service", "port": 8002, "role": "Participantes", "url": PARTICIPANTS_URL},
    {"name": "Registration Service", "port": 8003, "role": "Inscrições", "url": REGISTRATIONS_URL},
]
WEB_DIR = Path(__file__).with_name("static")
app = FastAPI(title="Confera - API Gateway", version="1.0.0")
app.mount("/static", StaticFiles(directory=WEB_DIR), name="static")

@app.get("/")
def index():
    return FileResponse(WEB_DIR / "index.html")

async def check_service(client: httpx.AsyncClient, service: dict) -> dict:
    """Consulta GET /health do serviço e devolve online/offline."""
    try:
        response = await client.get(f"{service['url']}/health")
        online = response.status_code == 200
    except httpx.HTTPError:
        online = False
    return {"name": service["name"], "port": service["port"], "role": service["role"],
            "status": "online" if online else "offline"}


@app.get("/services")
async def services():
    """Lista o gateway e os três microsserviços com porta e status."""
    async with httpx.AsyncClient(timeout=2) as client:
        checked = await asyncio.gather(*(check_service(client, s) for s in SERVICES))
    gateway = {"name": "API Gateway", "port": 8000, "role": "Entrada única e roteamento", "status": "online"}
    return [gateway, *checked]


async def proxy(request: Request, base_url: str, resource: str, path: str = ""):
    url = f"{base_url}/{resource}" + (f"/{path}" if path else "")
    body = await request.body()
    headers = {"content-type": request.headers.get("content-type","application/json")}
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            upstream = await client.request(request.method,url,params=dict(request.query_params),
                content=body or None,headers=headers)
    except httpx.HTTPError as exc:
        raise HTTPException(status_code=503,detail="Serviço indisponível.") from exc
    return Response(content=upstream.content,status_code=upstream.status_code,
                    media_type=upstream.headers.get("content-type","application/json"))

@app.api_route("/events",methods=["GET","POST"])
@app.api_route("/events/{path:path}",methods=["GET","PUT","DELETE"])
async def events(request: Request,path: str = ""):
    return await proxy(request,EVENTS_URL,"events",path)

@app.api_route("/participants",methods=["GET","POST"])
@app.api_route("/participants/{path:path}",methods=["GET","PUT","DELETE"])
async def participants(request: Request,path: str = ""):
    return await proxy(request,PARTICIPANTS_URL,"participants",path)

@app.api_route("/registrations",methods=["GET","POST"])
@app.api_route("/registrations/{path:path}",methods=["GET","PATCH"])
async def registrations(request: Request,path: str = ""):
    return await proxy(request,REGISTRATIONS_URL,"registrations",path)
