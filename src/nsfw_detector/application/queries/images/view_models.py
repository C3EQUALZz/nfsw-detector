from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True, slots=True)
class NSFWImageInformation:
    request_id: str
    status: Literal["success", "error", "processing"]
    output: str
