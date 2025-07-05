from typing import Final, Any

from aiohttp import ClientSession, ClientTimeout, FormData
from typing_extensions import override

from nsfw_detector.infrastructure.clients.http.base import HttpClient, HttpResponse, DataForForm


class AioHTTPClient(HttpClient):
    def __init__(self, session: ClientSession) -> None:
        self._session: Final[ClientSession] = session

    @override
    async def get(
            self,
            url: str,
            headers: dict[str, str] | None = None,
            params: dict[str, Any] | None = None,
            timeout: float | None = None
    ) -> HttpResponse:
        async with self._session.get(
                url,
                headers=headers,
                params=params,
                timeout=ClientTimeout(timeout)
        ) as response:
            return HttpResponse(
                status=response.status,
                body=await response.read(),
                headers=response.headers,
            )

    @override
    async def post(
            self,
            url: str,
            data: str | bytes | None = None,
            json_data: dict[str, Any] = None,
            headers: dict[str, str] | None = None,
            timeout: float | None = None
    ) -> HttpResponse:
        async with self._session.post(
                url,
                data=data,
                json=json_data,
                headers=headers,
                timeout=ClientTimeout(timeout)
        ) as response:
            return HttpResponse(
                status=response.status,
                body=await response.read(),
                headers=response.headers,
            )

    @override
    async def post_with_form(
            self,
            url: str,
            form_data: list[DataForForm],
            headers: dict[str, str] | None = None,
            timeout: float | None = None
    ) -> HttpResponse:
        form: FormData = FormData()

        for data in form_data:
            form.add_field(
                name=data.field_name,
                value=data.value,
                content_type=data.content_type,
            )

        async with self._session.post(
                url=url,
                headers=headers,
                data=form,
                timeout=ClientTimeout(timeout)
        ) as response:
            return HttpResponse(
                status=response.status,
                body=await response.read(),
                headers=response.headers,
            )
