import asyncio
import time
from concurrent.futures import ProcessPoolExecutor

@asyncio.coroutine
def coro(loop):
    ex = ProcessPoolExecutor(2)
    yield from loop.run_in_executor(ex, time.sleep, 10)  # This can be interrupted.

loop = asyncio.get_event_loop()
loop.run_until_complete(asyncio.wait_for(coro(loop), 1))

