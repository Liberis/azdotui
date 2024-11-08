# utils/debounce.py

import asyncio


def debounce(wait):
    def decorator(fn):
        last_call = None

        async def debounced(*args, **kwargs):
            nonlocal last_call
            if last_call:
                last_call.cancel()
            last_call = asyncio.create_task(asyncio.sleep(wait))
            try:
                await last_call
                await fn(*args, **kwargs)
            except asyncio.CancelledError:
                pass

        return debounced
    return decorator

