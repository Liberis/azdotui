# utils/helpers.py

import asyncio


async def call_async_if_coroutine(obj, method_name, *args):
    if hasattr(obj, method_name):
        method = getattr(obj, method_name)
        if asyncio.iscoroutinefunction(method):
            return await method(*args)
        else:
            return method(*args)
    else:
        raise AttributeError(f"{obj} does not have method {method_name}")

