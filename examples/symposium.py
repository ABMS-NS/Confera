from typing import Any
from framework.base import EventFramework

class Symposium(EventFramework):
    def configure(self, data: dict[str, Any]) -> dict[str, Any]:
        configured = dict(data)
        configured["category"] = "Simpósio Científico"
        return configured
