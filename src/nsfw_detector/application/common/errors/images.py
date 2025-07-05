from nsfw_detector.application.common.errors.base import ApplicationError


class NotAllowedExtensionOfImage(ApplicationError):
    ...


class FailedToProcessImage(ApplicationError):
    ...


