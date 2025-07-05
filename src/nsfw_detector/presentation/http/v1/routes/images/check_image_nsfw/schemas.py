from typing import Literal

from pydantic import BaseModel, Field


class CheckImageIsNSFWResponseSchema(BaseModel):
    status: Literal["OK", "REJECTED"] = Field(
        default="OK",
        min_length=1,
        max_length=255,
        description="Status of the check for frontend"
    )
    reason: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
        description="Reason of the check if it is not OK"
    )
