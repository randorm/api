import atexit
import sys
from contextlib import contextmanager
from contextvars import ContextVar
from uuid import UUID, uuid4

from loguru._logger import Core
from loguru._logger import Logger as LoguruLogger

COR_ID: ContextVar[UUID | None] = ContextVar("COR_ID", default=None)


class Logger(LoguruLogger):
    def __init__(self, context: str):
        super().__init__(
            core=Core(),
            exception=None,
            depth=0,
            record=False,
            lazy=False,
            colors=False,
            raw=False,
            capture=True,
            patchers=[],
            extra={"context": context, "correlation_id": ""},
        )
        logger_format = (
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green>|"
            "<level>{level: <8}</level>|"
            "<red><i>{extra[context]: <25}</i></red>|"
            "<magenta><bold>COR_ID: {extra[correlation_id]: <32}</bold></magenta>| "
            "<level>{message}</level>"
        )
        self.add(sys.stderr, format=logger_format)
        atexit.register(self.remove)

    def _start_record(self, name: str) -> str:
        return f"activity [{name}] started."

    def _fail_record(self, name: str, err: Exception) -> str:
        return f"activity [{name}] failed with {type(err).__name__}: {err}"

    def _error_record(self, name: str, err: Exception) -> str:
        return f"activity [{name}] raised error: {err}"

    def _finish_record(self, name: str) -> str:
        return f"activity [{name}] finished."

    @property
    def cor_id(self) -> str | None:
        cor_id = COR_ID.get()
        return cor_id.hex if cor_id is not None else ""

    def trace(self, message, *args, **kwargs):
        if self.cor_id:
            kwargs["correlation_id"] = self.cor_id
        super().trace(message, *args, **kwargs)

    def debug(self, message, *args, **kwargs):
        if self.cor_id:
            kwargs["correlation_id"] = self.cor_id
        super().debug(message, *args, **kwargs)

    def info(self, message, *args, **kwargs):
        if self.cor_id:
            kwargs["correlation_id"] = self.cor_id
        super().info(message, *args, **kwargs)

    def warning(self, message, *args, **kwargs):
        if self.cor_id:
            kwargs["correlation_id"] = self.cor_id
        super().warning(message, *args, **kwargs)

    def error(self, message, *args, **kwargs):
        if self.cor_id:
            kwargs["correlation_id"] = self.cor_id
        super().error(message, *args, **kwargs)

    def critical(self, message, *args, **kwargs):
        if self.cor_id:
            kwargs["correlation_id"] = self.cor_id
        super().critical(message, *args, **kwargs)

    @contextmanager
    def activity(self, name: str, with_traceback: bool = False, capture: bool = False):
        COR_ID.set(uuid4())

        try:
            self.info(self._start_record(name))
            yield
        except Exception as e:
            self.error(self._fail_record(name, e))

            if with_traceback:
                self.opt(exception=e).error(self._error_record(name, e))

            if not capture:
                raise e
        else:
            self.info(self._finish_record(name))
        finally:
            COR_ID.set(None)
