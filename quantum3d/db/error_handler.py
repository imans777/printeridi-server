
# db query exception handler
import functools


def message(func, e):
    try:
        print("ERROR db in function '", func.__name__, "' -> ", str(e))
    except:
        print("ERROR db in function '", func.__name__, "' -> ", str(e))


def error_handler_with(handler):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                return handler(func, e)
        return wrapper
    return decorator
