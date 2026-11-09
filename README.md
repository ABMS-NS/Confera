# Documentação técnica do código

## Ambiente

- Python 3.12 ou superior
- Dependências declaradas em `requirements.txt`: FastAPI, Uvicorn e HTTPX
- Persistência SQLite pela biblioteca padrão do Python

Instalação e execução a partir da raiz:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python run_all.py
```

No PowerShell, ative o ambiente com `.venv\\Scripts\\Activate.ps1`. O comando `python run_all.py` inicia os quatro processos da API principal. A interface do Gateway fica em `http://127.0.0.1:8000`.

Para encerrar os processos iniciados pelo script, use Ctrl+C.

## Mapa de módulos

| Caminho | Elementos documentados |
|---|---|
| `framework/base.py` | Classe abstrata `EventFramework`, Template Method e hotspots |
| `framework/interfaces.py` | Contratos dos componentes de evento, participante e inscrição |
| `framework/components.py` | Implementações reutilizáveis desses contratos |
| `framework/models.py` | Modelo de dados `Event` |
| `examples/` | Perfis SECOMP e Symposium registrados para o serviço de eventos |
| `services/events/main.py` | API de eventos |
| `services/participants/main.py` | API de participantes |
| `services/registrations/main.py` | API de inscrições |
| `gateway/main.py` | Rotas de entrada, proxy e verificação de disponibilidade |
| `gateway/static/` | Interface HTML, estilos CSS e lógica JavaScript |
| `demonstracoes/` | Aplicações independentes Workshop e Hackathon |
| `tests/` | Testes automatizados |
| `docs/diagrams/` | Diagramas PlantUML e imagens renderizadas |

## Framework de eventos

### `EventFramework`

A classe abstrata está em `framework/base.py`. Seu método `create_event(data)` define a ordem de criação:

1. `validate(data)`: exige valores não vazios para `name`, `date` e `location`.
2. `configure(data)`: hotspot abstrato. Cada classe derivada define a categoria e pode adaptar os dados.
3. `check_rules(data)`: hotspot opcional. A implementação padrão não acrescenta regras.
4. `event_component.create(data)`: constrói o objeto final pelo componente configurado no construtor.

As classes derivadas implementam `configure`. Podem sobrescrever `check_rules` quando precisarem validar uma condição específica. Os dados de entrada são dicionários com chaves como `name`, `description`, `date` e `location`.

### Perfis registrados em `examples/`

- `Secomp`, em `examples/secomp.py`: define a categoria `Semana Acadêmica` e mantém o comportamento padrão de `check_rules`.
- `Symposium`, em `examples/symposium.py`: define a categoria `Simpósio Científico` e exige descrição com pelo menos 20 caracteres.
- `examples/__init__.py`: fornece o registro e a função de seleção usados pelo Event Service. O campo `application` seleciona `secomp` ou `symposium`.

### Interfaces e componentes

As interfaces de `framework/interfaces.py` definem os contratos:

| Interface | Operação | Retorno |
|---|---|---|
| `EventInterface` | `create(data)` | Evento criado como dicionário |
| `ParticipantInterface` | `validate(data)` | Nome e e-mail normalizados |
| `RegistrationInterface` | `validate(data)` | IDs de evento e participante normalizados |

As implementações de `framework/components.py` são:

- `EventComponent`: instancia o modelo `Event`, remove espaços externos dos campos de texto e devolve `to_dict()`.
- `ParticipantComponent`: exige nome e valida e-mail por presença de `@` e de ponto no domínio.
- `RegistrationComponent`: converte `event_id` e `participant_id` para inteiros positivos.

As validações dos componentes lançam `ValueError` quando os dados não atendem às regras.

## Aplicações em `demonstracoes/`

Workshop e Hackathon são aplicações executáveis independentes. Os arquivos de entrada são `demonstracoes/workshop/main.py` e `demonstracoes/hackathon/main.py`. Ambos derivam de `EventFramework` e fornecem sua configuração e regra específica.

| Aplicação | Porta | Categoria | Regra | Inscrições |
|---|---:|---|---|---|
| Workshop | 8101 | Oficina | Nome com até 60 caracteres | Sim |
| Hackathon | 8102 | Maratona de Programação | Descrição com pelo menos 40 caracteres | Não |

As duas páginas são definidas separadamente em seus módulos `pagina.py`. A criação de rotas e o backend comum ficam em `demonstracoes/comum/servidor.py`; a persistência e inicialização do SQLite ficam em `demonstracoes/comum/banco.py`.

Cada aplicação usa um banco próprio. Workshop cria as tabelas de eventos, participantes e inscrições. Hackathon cria somente a tabela de eventos. Os caminhos podem ser definidos pelas variáveis `CONFERA_WORKSHOP_DB` e `CONFERA_HACKATHON_DB`.

Para iniciar as duas demonstrações:

```bash
python demonstracoes/run_all.py
```

Acesse `http://127.0.0.1:8101` para Workshop e `http://127.0.0.1:8102` para Hackathon. Para iniciar uma delas separadamente:

```bash
python -m demonstracoes.workshop.main
python -m demonstracoes.hackathon.main
```

Rotas de Workshop:

| Método e caminho | Operação |
|---|---|
| `GET /` | Página da aplicação |
| `GET /health` | Estado da aplicação |
| `GET /api/eventos` | Lista eventos |
| `POST /api/eventos` | Cria evento pelo framework |
| `DELETE /api/eventos/{id}` | Remove evento |
| `GET /api/participantes` | Lista participantes |
| `POST /api/participantes` | Cria participante pelo componente |
| `DELETE /api/participantes/{id}` | Remove participante |
| `GET /api/inscricoes` | Lista inscrições |
| `POST /api/inscricoes` | Cria inscrição pelo componente |
| `PATCH /api/inscricoes/{id}/cancelar` | Cancela inscrição ativa |

Hackathon expõe `/`, `/health` e as rotas de eventos. Rotas de participantes e inscrições não são registradas nessa aplicação.

## APIs principais

Os serviços FastAPI podem ser consultados diretamente em suas portas. A interface web utiliza o Gateway na porta 8000.

### Event Service, porta 8001

Arquivo: `services/events/main.py`. Usa `events.db` e integra o registro de perfis de `examples/` ao framework.

| Método e caminho | Operação |
|---|---|
| `GET /health` | Estado do serviço |
| `GET /events` | Lista eventos |
| `POST /events` | Cria evento; requer `application` |
| `GET /events/{id}` | Consulta evento |
| `PUT /events/{id}` | Atualiza evento |
| `DELETE /events/{id}` | Remove evento |

O corpo de criação inclui `name`, `date`, `location`, `application` e, opcionalmente, `description`. Os valores aceitos para `application` são `secomp` e `symposium`.

### Participant Service, porta 8002

Arquivo: `services/participants/main.py`. Usa `participants.db` e `ParticipantComponent`.

| Método e caminho | Operação |
|---|---|
| `GET /health` | Estado do serviço |
| `GET /participants` | Lista participantes |
| `POST /participants` | Cria participante |
| `GET /participants/{id}` | Consulta participante |
| `PUT /participants/{id}` | Atualiza participante |
| `DELETE /participants/{id}` | Remove participante |

O corpo de criação ou atualização contém `name` e `email`. E-mail repetido retorna HTTP 409.

### Registration Service, porta 8003

Arquivo: `services/registrations/main.py`. Usa `registrations.db` e `RegistrationComponent`. Antes de criar inscrição, consulta Event Service e Participant Service por HTTP.

| Método e caminho | Operação |
|---|---|
| `GET /health` | Estado do serviço |
| `POST /registrations` | Cria inscrição ativa |
| `GET /registrations` | Lista inscrições |
| `GET /registrations?event_id={id}` | Filtra por evento |
| `GET /registrations?status=active` | Filtra por estado |
| `PATCH /registrations/{id}/cancel` | Cancela inscrição ativa |

O corpo de criação contém `event_id` e `participant_id`. O serviço rejeita IDs inválidos, referências inexistentes e inscrição ativa duplicada. Os estados aceitos no filtro são `active` e `cancelled`.

### API Gateway, porta 8000

Arquivo: `gateway/main.py`. Serve `gateway/static/index.html`, publica os arquivos de `gateway/static/` e encaminha as rotas para os serviços correspondentes.

- `GET /`: entrega a interface.
- `GET /services`: consulta `/health` nos serviços e retorna nome, porta, função e estado.
- `/events` e `/events/{path}`: encaminha operações de evento.
- `/participants` e `/participants/{path}`: encaminha operações de participante.
- `/registrations` e `/registrations/{path}`: encaminha operações de inscrição.
- Serviço de destino indisponível: retorna HTTP 503.

A documentação OpenAPI do FastAPI fica em `/docs` em cada porta: 8000, 8001, 8002 e 8003.

## Inicialização dos serviços

O script `run_all.py` inicia os serviços nas portas 8001, 8002, 8003 e o Gateway na porta 8000:

```bash
python run_all.py
```

Inicialização manual, em terminais separados:

```bash
uvicorn services.events.main:app --port 8001 --reload
uvicorn services.participants.main:app --port 8002 --reload
uvicorn services.registrations.main:app --port 8003 --reload
uvicorn gateway.main:app --port 8000 --reload
```

## Testes

Executar a suíte com:

```bash
python -m unittest discover -s tests -v
```

Os arquivos de teste estão em `tests/test_framework.py`, `tests/test_api.py` e `tests/test_demonstracoes.py`.

## Persistência e comunicação entre serviços

Cada microsserviço mantém seu banco SQLite local. Registration Service guarda os identificadores de evento e participante e valida sua existência por chamadas HTTP antes de criar uma inscrição. Não há chaves estrangeiras entre bancos nem transação distribuída. Uma falha ou condição de corrida pode ocorrer entre a consulta remota e a gravação local.

## Referências de implementação

- Diagrama do framework: `docs/diagrams/framework.puml`
- Diagrama dos componentes: `docs/diagrams/components.puml`
- Diagrama de microsserviços: `docs/diagrams/microservices.puml`
- Detalhes de extensão do framework: `docs/third_application.md`
