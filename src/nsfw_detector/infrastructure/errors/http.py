from nsfw_detector.infrastructure.errors.base import InfrastructureError


class NoFieldFoundInHTTPRequestError(InfrastructureError):
    ...


class ServiceUnAvailableError(InfrastructureError):
    ...
