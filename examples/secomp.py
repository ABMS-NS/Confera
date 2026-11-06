from typing import Any
from framework.base import EventFramework

class Secomp(EventFramework):
    def configure(self, data: dict[str, Any]) -> dict[str, Any]:
        configured = dict(data)
        configured["category"] = "Semana Acadêmica"
        return configured
