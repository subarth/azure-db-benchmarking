import asyncio

class AsyncAtomicInt:
    def __init__(self, initial=0):
        self._value = initial
        self._lock = asyncio.Lock()

    async def increment(self, n=1):
        async with self._lock:
            self._value += n
            return self._value

    async def get(self):
        async with self._lock:
            return self._value

    async def reset(self):
        async with self._lock:
            self._value = 0