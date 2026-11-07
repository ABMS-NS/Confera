# Criando uma nova aplicação (passo a passo)

Exemplo: uma aplicação **Workshop** (oficinas) que exige descrição e limita o nome do evento.

## Passo 1 — Criar a classe herdando o framework (`examples/workshop.py`)

```python
from typing import Any
from framework.base import EventFramework


class Workshop(EventFramework):
    # HOTSPOT 1 (obrigatório): define a categoria.
    def configure(self, data: dict[str, Any]) -> dict[str, Any]:
        configured = dict(data)
        configured["category"] = "Oficina"
        return configured

    # HOTSPOT 2 (opcional): regra própria da aplicação.
    def check_rules(self, data: dict[str, Any]) -> None:
        if len(str(data["name"])) > 60:
            raise ValueError("O nome da oficina deve ter no máximo 60 caracteres.")
```

## Passo 2 — Registrar a aplicação (`examples/__init__.py`)

```python
from .workshop import Workshop

APPLICATIONS = {"secomp": Secomp, "symposium": Symposium, "workshop": Workshop}
```

## Passo 3 — Expor na interface (`gateway/static/index.html`)

```html
<option value="workshop">Oficina</option>
```

## Passo 4 — Usar

```python
from examples import get_application

event = get_application("workshop").create_event({
    "name": "Oficina de Python", "description": "Atividade prática",
    "date": "2026-12-10", "location": "UFAL",
})
print(event["category"])  # Oficina
```

A nova classe **não reescreve** a validação comum, a ordem dos passos nem a
criação do evento: tudo isso vem do framework. Só os hotspots são implementados.
