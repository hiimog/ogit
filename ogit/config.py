import dataclasses
from typing import *
from uuid import UUID

@dataclasses.dataclass
class LogConfig:
    level: Literal["debug", "info", "warn", "error"]
    sinks: Literal["seq", "file"]
    filters: List[str]
    file: Optional[str]


@dataclasses.dataclass
class Config:
    logging: LogConfig
    correlation_id: UUID
