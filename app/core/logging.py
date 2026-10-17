import logging
import sys
from contextvars import ContextVar

# Set per request by app.core.errors; "-" outside a request (startup, scripts).
request_id_var: ContextVar[str] = ContextVar("request_id", default="-")


class RequestIdFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id_var.get()
        return True


def configure_logging(debug: bool = False) -> None:
    level = logging.DEBUG if debug else logging.INFO
    handler = logging.StreamHandler(sys.stdout)
    handler.addFilter(RequestIdFilter())
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)s | %(request_id)s | %(name)s | %(message)s",
        handlers=[handler],
        force=True,
    )
