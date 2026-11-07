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

Forma rápida (sobe os 4 processos de uma vez):

```
python run_all.py
```

Ou, manualmente, em quatro terminais na raiz:
```bash
uvicorn services.events.main:app --port 8001 --reload
uvicorn services.participants.main:app --port 8002 --reload
uvicorn services.registrations.main:app --port 8003 --reload
uvicorn gateway.main:app --port 8000 --reload
```
Acesse http://127.0.0.1:8000. Testes: `python -m unittest discover -s tests -v`.

## Como o reúso funciona (resumo)

`EventFramework.create_event()` é o **Template Method**: valida → `configure()` → `check_rules()` → cria o evento.
`configure()` (obrigatório) e `check_rules()` (opcional) são os **hotspots**. O resto é **frozen spot**.

| Aplicação | Categoria (hotspot 1) | Regra própria (hotspot 2) |
|---|---|---|
| SECOMP | Semana Acadêmica | nenhuma (herda o padrão) |
| Simpósio | Simpósio Científico | descrição com ≥ 20 caracteres |

Passo a passo para criar uma terceira aplicação: [`docs/third_application.md`](docs/third_application.md).

## API (via gateway, porta 8000)

`GET /services` · `/events` (`application` obrigatório: `secomp` ou `symposium`) · `/participants` · `/registrations`.
Documentação interativa de cada serviço em `http://127.0.0.1:800X/docs`.

## Limitações
Cada serviço possui seu próprio SQLite. Inscrições guardam IDs sem foreign keys entre bancos. Não há transação distribuída; a validação prévia dos IDs não elimina falhas ou condições de corrida. Projeto didático, sem autenticação, pagamentos, e-mails ou certificados.
