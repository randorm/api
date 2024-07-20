import atexit
import sys
from contextlib import contextmanager
from uuid import uuid4

from loguru._logger import Core
from loguru._logger import Logger as LoguruLogger


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
            extra={"context": context, "correlation_id": None},
        )
        logger_format = (
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}:{function}:{line}</cyan> | "
            "<red>[<i>{extra[context]}</i>]</red> "
            "<magenta>[<bold>COR_ID: {extra[correlation_id]}</bold>]</magenta> "
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

    @contextmanager
    def activity(
        self,
        name: str,
        with_traceback: bool = False,
        capture: bool = False,
        with_correlation_id: bool = True,
    ):
        if with_correlation_id:
            correlation_id = uuid4().hex
        else:
            correlation_id = None

        try:
            self.info(self._start_record(name), correlation_id=correlation_id)
            yield
        except Exception as e:
            self.error(self._fail_record(name, e), correlation_id=correlation_id)

            if with_traceback:
                self.opt(exception=e).error(
                    self._error_record(name, e), correlation_id=correlation_id
                )

            if not capture:
                raise e
        else:
            self.info(self._finish_record(name), correlation_id=correlation_id)
