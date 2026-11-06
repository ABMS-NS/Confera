# Confera
Framework acadêmico para gerenciamento de eventos científicos com reúso por framework orientado a objetos, componentes e microservices.

Duas aplicações demonstrativas reutilizam o mesmo núcleo: **SECOMP** (Semana Acadêmica) e **Simpósio** (Simpósio Científico).

## Tecnologias
Python 3.12+, FastAPI, SQLite, httpx, HTML/CSS/JavaScript puro, Uvicorn e PlantUML.

## Estrutura
- `framework/`: interfaces, componentes e Template Method.
- `examples/`: aplicações concretas.
- `services/`: eventos, participantes e inscrições.
- `gateway/`: API Gateway e interface web.
- `tests/`: testes unitários.
- `docs/`: arquitetura, backlog e diagramas.

## Instalação
```bash
python -m venv .venv
# Linux/macOS: source .venv/bin/activate
# Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Abra quatro terminais na raiz:
```bash
uvicorn services.events.main:app --port 8001 --reload
uvicorn services.participants.main:app --port 8002 --reload
uvicorn services.registrations.main:app --port 8003 --reload
uvicorn gateway.main:app --port 8000 --reload
```
Acesse http://127.0.0.1:8000. Testes: `python -m unittest discover -s tests -v`.

## Limitações
Cada serviço possui seu próprio SQLite. Inscrições guardam IDs sem foreign keys entre bancos. Não há transação distribuída; a validação prévia dos IDs não elimina falhas ou condições de corrida. Projeto didático, sem autenticação, pagamentos, e-mails ou certificados.
