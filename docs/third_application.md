# Criando uma terceira aplicação

Exemplo: criar uma aplicação de oficinas em `examples/workshop.py`:

```python
from typing import Any
from framework.base import EventFramework

class Workshop(EventFramework):
    def configure(self, data: dict[str, Any]) -> dict[str, Any]:
        configured = dict(data)
        configured["category"] = "Oficina"
        return configured
```

Uso:

```python
from examples.workshop import Workshop

event = Workshop().create_event({
    "name": "Oficina de Python",
    "description": "Atividade prática",
    "date": "2026-12-10",
    "location": "UFAL",
})
print(event)
```

A nova classe reutiliza a validação, o fluxo de criação e o componente de eventos. Apenas o hotspot `configure()` precisa ser implementado.
