import ogit.config as oc
import typing as t
import uuid as u

LOG_LEVELS = frozenset(["debug", "info", "warn", "error"])
NUM_LEVELS = len(LOG_LEVELS)
LOG_LEVEL_LOOKUP = {l: i for (l, i) in zip(LOG_LEVELS, range(NUM_LEVELS))}
LogLevel = t.Union[LOG_LEVELS]
LazyMsg = t.Callable[[], t.Tuple[str, t.Dict[str, t.Any]]]


class Logger:
    def __init__(self, level: LogLevel):
        self._level = level

    def log(self, location: u.UUID, err: t.Optional[Exception], level: LogLevel, msg: str, **kwargs):
        pass

    def log_lazy(self, location: u.UUID, err: t.Optional[Exception], level: LogLevel, msg: LazyMsg):
        pass

    def debug(self, location: u.UUID, level: LogLevel, msg: str, **kwargs):
        pass

    def debug_lazy(self, location: u.UUID, level: LogLevel, msg: LazyMsg):
        pass

    def info(self, location: u.UUID, level: LogLevel, msg: str, **kwargs):
        pass

    def info_lazy(self, location: u.UUID, level: LogLevel, msg: LazyMsg):
        pass

    def warn(self, location: u.UUID, err: t.Optional[Exception], level: LogLevel, msg: str, **kwargs):
        pass

    def warn_lazy(self, location: u.UUID, err: t.Optional[Exception], level: LogLevel, msg: LazyMsg):
        pass

    def error(self, location: u.UUID, err: t.Optional[Exception], level: LogLevel, msg: str, **kwargs):
        pass

    def error_lazy(self, location: u.UUID, err: t.Optional[Exception], level: LogLevel, msg: LazyMsg):
        pass






def create_logger(config: oc.Config) -> Logger:
    return Logger()
