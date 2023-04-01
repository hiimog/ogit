import re

import orjson

import ogit.config as oc
import typing as t
from datetime import datetime
import requests

DEBUG = "debug"
INFO = "info"
WARN = "warn"
ERROR = "error"
OFF = "off"
LOG_LEVELS = frozenset([DEBUG, INFO, WARN, ERROR, OFF])

NUM_LEVELS = len(LOG_LEVELS)
LOG_LEVEL_LOOKUP = {l: i for (l, i) in zip(LOG_LEVELS, range(NUM_LEVELS))}
LogLevel = t.Union[LOG_LEVELS]
LazyMsg = t.Callable[[], t.Tuple[str, t.Dict[str, t.Any]]]

_uuid_regex = re.compile("^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$")


class Logger:
    def __init__(self, log_config: oc.LogConfig):
        self._level = log_config.level

    def _should_log(self, requested_level: LogLevel):
        if requested_level == OFF:
            return False
        min_level, want_level = LOG_LEVEL_LOOKUP[self._level], LOG_LEVEL_LOOKUP[requested_level]
        return want_level >= min_level

    def _write(self, body: dict):
        bytes = orjson.dumps(body)
        headers = {"Content-Type": "application/json"}
        res = requests.post("http://localhost:5341/api/events/raw?clef", data=bytes, headers=headers)
        assert res.ok

    def _log(self, location: str, err: t.Optional[Exception], level: LogLevel, msg: str, **kwargs):
        if not _uuid_regex.match(location):
            raise ValueError("location must be valid lower case uuid")
        if not self._should_log(level):
            return

        kwargs["loc"] = location
        body = {
            "@t": datetime.utcnow().isoformat() + "Z",
            "@m": msg,
            **kwargs
        }
        if err:
            body["@x"] = str(err)
        self._write(body)

    def _log_lazy(self, location: str, err: t.Optional[Exception], level: LogLevel, msg: LazyMsg):
        if not _uuid_regex.match(location):
            raise ValueError("location must be valid lower case uuid")
        if not self._should_log(level):
            return
        lazy_msg, lazy_kwargs = msg()
        lazy_kwargs["loc"] = location
        body = {
            "@t": datetime.utcnow().isoformat() + "Z",
            "@m": msg,
            **lazy_kwargs
        }
        if err:
            body["@x"] = str(err)
        self._write(body)

    def debug(self, location: str, msg: str, **kwargs):
        self._log(location, None, DEBUG, msg, **kwargs)

    def debug_lazy(self, location: str, msg: LazyMsg):
        self._log_lazy(location, None, DEBUG, msg)

    def info(self, location: str, msg: str, **kwargs):
        self._log(location, None, INFO, msg, **kwargs)

    def info_lazy(self, location: str, msg: LazyMsg):
        self._log_lazy(location, None, INFO, msg)

    def warn(self, location: str, err: t.Optional[Exception], msg: str, **kwargs):
        self._log(location, err, WARN, msg, **kwargs)

    def warn_lazy(self, location: str, err: t.Optional[Exception], msg: LazyMsg):
        self._log_lazy(location, err, WARN, msg)

    def error(self, location: str, err: t.Optional[Exception], msg: str, **kwargs):
        self._log(location, err, ERROR, msg, **kwargs)

    def error_lazy(self, location: str, err: t.Optional[Exception], msg: LazyMsg):
        self._log_lazy(location, err, ERROR, msg)


def create_logger(config: oc.Config) -> Logger:
    return Logger(config.logging)
