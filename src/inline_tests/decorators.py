from functools import wraps
from typing import Callable, Optional, Any


def test(*, tag: Optional[str] = None):
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        wrapper._is_test = True
        wrapper._tag = tag
        return wrapper

    return decorator


def before_each(func: Callable) -> Callable:
    func._is_before_each = True
    return func


def after_each(func: Callable) -> Callable:
    func._is_after_each = True
    return func
