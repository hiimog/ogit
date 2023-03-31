import dataclasses
from typing import *


@dataclasses.dataclass
class LogConfig:
    level: Literal["debug", "info", "warn", "error"]
    sinks: Literal["seq", "file"]
    filters: List[str]
    file: Optional[str]


@dataclasses.dataclass
class Config:
    logging: LogConfig
