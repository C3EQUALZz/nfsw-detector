import json
from abc import abstractmethod
from dataclasses import dataclass, field
from typing import Any, Protocol


@dataclass(frozen=True, slots=True)
class HttpResponse:
    status: int
    headers: dict[str, str]
    body: bytes

    def text(self) -> str:
        return self.body.decode('utf-8')

    def json(self) -> Any:
        return json.loads(self.body)


@dataclass(frozen=True, slots=True)
class DataForForm:
    field_name: str
    value: Any
    content_type: str | None = field(default=None)


class HttpClient(Protocol):
    @abstractmethod
    async def get(
            self,
            url: str,
            headers: dict[str, str] | None = None,
            params: dict[str, Any] | None = None,
            timeout: float | None = None
    ) -> HttpResponse:
        ...

    @abstractmethod
    async def post(
            self,
            url: str,
            data: str | bytes | None = None,
            json_data: dict[str, Any] = None,
            headers: dict[str, str] | None = None,
            timeout: float | None = None
    ) -> HttpResponse:
        ...

    @abstractmethod
    async def post_with_form(
            self,
            url: str,
            form_data: list[DataForForm],
            headers: dict[str, str] | None = None,
            timeout: float | None = None
    ) -> HttpResponse:
        ...
