import re
from typing import *
from datetime import datetime
from uuid import UUID
from orjson import dumps
from requests import post

import ogit.config as oc

DEBUG = "debug"
INFO = "info"
WARN = "warn"
ERROR = "error"
OFF = "off"
LOG_LEVELS = frozenset([DEBUG, INFO, WARN, ERROR, OFF])

NUM_LEVELS = len(LOG_LEVELS)
LOG_LEVEL_LOOKUP = {l: i for (l, i) in zip(LOG_LEVELS, range(NUM_LEVELS))}
LogLevel = Union[LOG_LEVELS]
LazyMsg = Callable[[], Tuple[str, Dict[str, Any]]]

_uuid_regex = re.compile("^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$")


class Logger:
    def __init__(self, level: LogLevel, correlation_id: UUID):
        self._level = level
        self._correlation_id = correlation_id

    def _should_log(self, requested_level: LogLevel):
        if requested_level == OFF:
            return False
        min_level, want_level = LOG_LEVEL_LOOKUP[self._level], LOG_LEVEL_LOOKUP[requested_level]
        return want_level >= min_level

    def _write(self, body: dict):
        data = dumps(body)
        headers = {"Content-Type": "application/json"}
        res = post("http://localhost:5341/api/events/raw?clef", data=data, headers=headers)
        if res.status_code != 201:
            raise IOError("log creation failed with non 201 status")

    def _log(self, location: str, err: Optional[Exception], level: LogLevel, msg: str, extra: Dict[str, Any] = None):
        if not _uuid_regex.match(location):
            raise ValueError("location must be valid lower case uuid")
        if not self._should_log(level):
            return
        extra = extra or {}
        extra["loc"] = location
        extra["cor"] = self._correlation_id
        body = {
            "@t": datetime.utcnow().isoformat() + "Z",
            "@m": msg,
            "@l": level,
            **extra
        }
        if err:
            body["@x"] = str(err)
        self._write(body)

    def _log_lazy(self, location: str, err: Optional[Exception], level: LogLevel, msg: LazyMsg):
        if not _uuid_regex.match(location):
            raise ValueError("location must be valid lower case uuid")
        if not self._should_log(level):
            return
        lazy_msg, lazy_kwargs = msg()
        lazy_kwargs["loc"] = location
        lazy_kwargs["cor"] = self._correlation_id
        body = {
            "@t": datetime.utcnow().isoformat() + "Z",
            "@m": msg,
            "@l": level,
            **lazy_kwargs
        }
        if err:
            body["@x"] = str(err)
        self._write(body)

    def debug(self, location: str, msg: str, extra: Dict[str, Any] = None):
        self._log(location, None, DEBUG, msg, extra)

    def debug_lazy(self, location: str, msg: LazyMsg):
        self._log_lazy(location, None, DEBUG, msg)

    def info(self, location: str, msg: str, extra: Dict[str, Any] = None):
        self._log(location, None, INFO, msg, extra)

    def info_lazy(self, location: str, msg: LazyMsg):
        self._log_lazy(location, None, INFO, msg)

    def warn(self, location: str, err: Optional[Exception], msg: str, extra: Dict[str, Any] = None):
        self._log(location, err, WARN, msg, extra)

    def warn_lazy(self, location: str, err: Optional[Exception], msg: LazyMsg):
        self._log_lazy(location, err, WARN, msg)

    def error(self, location: str, err: Optional[Exception], msg: str, extra: Dict[str, Any] = None):
        self._log(location, err, ERROR, msg, extra)

    def error_lazy(self, location: str, err: Optional[Exception], msg: LazyMsg):
        self._log_lazy(location, err, ERROR, msg)


def create_logger(config: oc.Config) -> Logger:
    return Logger(config.logging.level, config.correlation_id)
