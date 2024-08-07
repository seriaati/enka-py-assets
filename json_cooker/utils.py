import logging
from typing import Any, Callable

LOGGER_ = logging.getLogger(__name__)


def async_error_handler(func: Callable[..., Any]) -> Callable[..., Any]:
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return await func(*args, **kwargs)
        except Exception:
            LOGGER_.exception("An error occurred while running %s", func.__name__)
            raise

    return wrapper
