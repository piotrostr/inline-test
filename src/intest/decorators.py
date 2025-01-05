from functools import wraps
from typing import Callable, Optional, Any


def test(*, tag: Optional[str] = None, skip: bool = False, skip_reason: str = ""):
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        wrapper._is_test = True
        wrapper._tag = tag
        wrapper._skip = skip
        wrapper._skip_reason = skip_reason
        return wrapper

    return decorator


def before_each(func: Callable) -> Callable:
    func._is_before_each = True
    return func


def after_each(func: Callable) -> Callable:
    func._is_after_each = True
    return func


def before_all(func: Callable) -> Callable:
    func._is_before_all = True
    return func


def after_all(func: Callable) -> Callable:
    func._is_after_all = True
    return func
