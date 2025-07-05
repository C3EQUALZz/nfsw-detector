import io
import logging
import json
from typing import Final, Any

from typing_extensions import override

from nsfw_detector.application.common.ports.images.query_gateway import ImageQueryGateway
from nsfw_detector.application.queries.images.view_models import NSFWImageInformation
from nsfw_detector.infrastructure.clients.http.base import HttpClient, HttpResponse, DataForForm
from nsfw_detector.infrastructure.errors.http import NoFieldFoundInHTTPRequestError, ServiceUnAvailableError
from nsfw_detector.setup.configs import GenAPIConfig

logger: Final[logging.Logger] = logging.getLogger(__name__)


class GenAIImageQueryGateway(ImageQueryGateway):
    def __init__(
            self,
            http_client: HttpClient,
            api_config: GenAPIConfig
    ) -> None:
        self._http_client: Final[HttpClient] = http_client
        self._api_config: Final[GenAPIConfig] = api_config

    @override
    async def check_image_is_nsfw_by_file(self, data: bytes) -> NSFWImageInformation | None:
        url: str = "https://api.gen-api.ru/api/v1/networks/image-nsfw-checker"
        logger.info(
            "Making request to checking nsfw content to %s",
            url
        )

        token: str = f"Bearer {self._api_config.api_key}"

        response: HttpResponse = await self._http_client.post_with_form(
            url=url,
            headers={
                "Accept": "application/json",
                "Authorization": token
            },
            form_data=[
                DataForForm(field_name="input", value=json.dumps({"is_sync": 1}), content_type="application/json"),
                DataForForm(field_name="image", value=io.BytesIO(data)),
            ],
        )

        logger.info("Received response from nsfw checker API: %s", response)

        if response.status >= 500:
            raise ServiceUnAvailableError("api.gen-api.ru not responding")

        data: Any = response.json()

        if not (request_id := data.get("request_id")):
            raise NoFieldFoundInHTTPRequestError(
                "request_id not found in response from url %s",
                url
            )

        if not (status := data.get("status")):
            raise NoFieldFoundInHTTPRequestError(
                "status not found in response from url %s",
                url
            )

        if not (output := data.get("output")):
            raise NoFieldFoundInHTTPRequestError(
                "output not found in response from url %s",
                url
            )

        return NSFWImageInformation(
            request_id=request_id,
            status=status,
            output=output
        )
