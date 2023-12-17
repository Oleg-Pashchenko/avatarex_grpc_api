import time
from functools import wraps


def timing_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"Синхронная функция {func.__name__} выполнялась {execution_time} секунд")
        return result

    return wrapper


def async_timing_decorator(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        result = await func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"Асинхронная функция {func.__name__} выполнялась {execution_time} секунд")
        return result

    return wrapper
