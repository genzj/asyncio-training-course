import asyncio
from datetime import datetime
from threading import Thread, current_thread


class AsyncThread(Thread):

    def __init__(self):
        super().__init__(name='AsyncThread')
        self.loop = asyncio.new_event_loop()

    def run(self) -> None:
        self.loop.run_forever()

    def schedule_task(self, task):
        return asyncio.run_coroutine_threadsafe(
            task, self.loop
        )


class MainThread(Thread):

    def __init__(self, async_thread: AsyncThread):
        super().__init__(name='MainThread')
        self.async_thread = async_thread
        self.begin_time = datetime.now()

    async def async_task(self, i: int) -> int:
        await asyncio.sleep(i)
        delta = datetime.now() - self.begin_time
        elapse = delta.total_seconds()
        print(
            f'task {i} completed in {current_thread().getName()} @{elapse}'
        )
        return i

    def run(self) -> None:
        for i in range(5):
            self.async_thread.schedule_task(self.async_task(i))
        print('exit main thread')


async_thread = AsyncThread()
main_thread = MainThread(async_thread)

async_thread.start()
main_thread.start()
