from dataclasses import asdict, dataclass
from typing import Any

@dataclass
class Event:
    name: str
    description: str
    date: str
    location: str
    category: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
