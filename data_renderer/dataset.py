from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import Any, Protocol


class DatasetProvider(Protocol):
    id: str
    name: str
    description: str

    def metadata(self) -> dict[str, str]: ...

    def load(self, filters: Mapping[str, str]) -> dict[str, Any]: ...


@dataclass(frozen=True)
class Dataset:
    id: str
    name: str
    description: str
    loader: Callable[[Mapping[str, str]], dict[str, Any]]

    def metadata(self) -> dict[str, str]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
        }

    def load(self, filters: Mapping[str, str]) -> dict[str, Any]:
        return self.loader(filters)
