from pathlib import Path
import httpx
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

EVENTS_URL = "http://127.0.0.1:8001"
PARTICIPANTS_URL = "http://127.0.0.1:8002"
REGISTRATIONS_URL = "http://127.0.0.1:8003"
WEB_DIR = Path(__file__).with_name("static")
app = FastAPI(title="Confera - API Gateway", version="1.0.0")
app.mount("/static", StaticFiles(directory=WEB_DIR), name="static")

@app.get("/")
def index():
    return FileResponse(WEB_DIR / "index.html")

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
