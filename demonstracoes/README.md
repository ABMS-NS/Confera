# Demonstrações de reúso

Duas aplicações independentes que reutilizam o mesmo framework de `framework/`.
Cada uma tem **página, CSS e JavaScript próprios**, com identidade visual
distinta — como se tivessem sido feitas por pessoas diferentes. O que se
compartilha é apenas o backend (`demonstracoes/comum/servidor.py`).

| Demonstração | Porta | Visual | Categoria | Inscrições | Hotspot 1 (`configure`) | Hotspot 2 (`check_rules`) |
|---|---|---|---|---|---|---|
| Workshop | 8101 | editorial, tons quentes, serifado | Oficina | **sim** | define a categoria | nome com no máximo 60 caracteres |
| Hackathon | 8102 | terminal, escuro, monoespaçado | Maratona de Programação | **não** | define a categoria | descrição com pelo menos 40 caracteres |

A diferença principal entre elas é o serviço de inscrição:

- **Workshop** habilita participantes e inscrições e, para isso, reutiliza
  também `ParticipantComponent` e `RegistrationComponent` (os mesmos
  componentes usados pelos microsserviços).
- **Hackathon** reutiliza apenas o framework de eventos; as rotas de
  participante/inscrição nem são registradas.

## Como rodar

Na raiz do repositório (com a venv ativa ou usando `.venv/bin/python`):

```bash
python demonstracoes/run_all.py
```

Depois abra:

- Workshop: <http://127.0.0.1:8101>
- Hackathon: <http://127.0.0.1:8102>

Também é possível subir separadamente:

```bash
python -m demonstracoes.workshop.main    # porta 8101
python -m demonstracoes.hackathon.main   # porta 8102
```

## O que cada página mostra

As páginas são voltadas ao usuário final: apenas títulos de seção e as partes
funcionais. Não exibem explicações sobre o reúso nem código-fonte.

**Workshop** — organizado como um caderno editorial:

1. nova oficina;
2. oficinas cadastradas;
3. **quem vai participar** (cadastro de participantes);
4. **inscrições** (inscrever, listar e cancelar).

**Hackathon** — organizado como um terminal, em seções numeradas:

1. criar evento;
2. eventos.

A criação de eventos passa pelo `create_event()` do framework nas duas
aplicações. A diferença é que o Hackathon não habilita o serviço de inscrição,
então nem as rotas nem a interface correspondente existem.

## API

Workshop (com inscrições):

| Rota | Descrição |
|---|---|
| `GET /` | Página HTML |
| `GET /health` | Status do app |
| `GET/POST /api/eventos` | Lista/cria eventos (criação via `create_event()`) |
| `DELETE /api/eventos/{id}` | Remove um evento |
| `GET/POST /api/participantes` | Lista/cria participantes (`ParticipantComponent`) |
| `DELETE /api/participantes/{id}` | Remove um participante |
| `GET/POST /api/inscricoes` | Lista/cria inscrições (`RegistrationComponent`) |
| `PATCH /api/inscricoes/{id}/cancelar` | Cancela uma inscrição ativa |

Hackathon (sem inscrições): apenas `/`, `/health` e as rotas de `/api/eventos`.
As rotas de participantes e inscrições retornam 404.

## Estrutura

```
demonstracoes/
├── comum/
│   ├── __init__.py
│   ├── banco.py          # conexão/criação das tabelas SQLite
│   └── servidor.py       # fábrica FastAPI compartilhada + regras de backend
├── workshop/
│   ├── main.py           # classe Workshop + wiring (com inscrições)
│   ├── pagina.py         # HTML/CSS/JS próprios (editorial)
│   └── workshop.db       # banco SQLite (criado ao iniciar)
├── hackathon/
│   ├── main.py           # classe Hackathon + wiring (sem inscrições)
│   ├── pagina.py         # HTML/CSS/JS próprios (terminal)
│   └── hackathon.db      # banco SQLite (criado ao iniciar)
├── run_all.py            # sobe as duas de uma vez
└── README.md
```

Cada `main.py` monta o app assim:

```python
app = create_demo_app(
    titulo="Workshop",
    aplicacao=Workshop,
    com_inscricoes=True,
    pagina=render,          # página própria de cada app
    caminho_banco=BANCO,    # arquivo SQLite da aplicação
)
```

O caminho do banco pode ser trocado pelas variáveis de ambiente
`CONFERA_WORKSHOP_DB` e `CONFERA_HACKATHON_DB` (os testes usam bancos
temporários).

## Persistência

Cada demonstração tem seu próprio arquivo SQLite, como os microsserviços:

| Aplicação | Arquivo | Tabelas |
|---|---|---|
| Workshop | `demonstracoes/workshop/workshop.db` | `eventos`, `participantes`, `inscricoes` |
| Hackathon | `demonstracoes/hackathon/hackathon.db` | apenas `eventos` |

Os arquivos são criados automaticamente na primeira execução e os dados
sobrevivem ao reinício do servidor. Como o Hackathon não habilita inscrições,
o banco dele nem possui as tabelas de participantes/inscrições. Os arquivos
`*.db` já estão no `.gitignore`; para zerar uma demo, basta parar o servidor e
apagar o arquivo correspondente.

Não há autenticação: as demonstrações servem para evidenciar o reúso, não para
produção.

## Por que não Astro?

O framework é Python: o Template Method e os componentes são executados no
servidor. Uma página Astro (ou qualquer geração estática) teria que reimplementar
a lógica em JavaScript, o que **duplicaria** o código em vez de demonstrar
reúso. Por isso as páginas são HTML simples servidas por FastAPI, chamando o
mesmo `framework/` que o Event Service usa.
