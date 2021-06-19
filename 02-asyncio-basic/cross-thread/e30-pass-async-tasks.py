import asyncio
from threading import Thread, current_thread


class AsyncThread(Thread):

    def __init__(self):
        super().__init__(name='AsyncThread')
        self.loop = asyncio.new_event_loop()

    def run(self) -> None:
        self.loop.run_forever()


class ControlThread(Thread):

    def __init__(self, async_thread: AsyncThread) -> None:
        super().__init__(name='ControlThread')
        self.async_thread = async_thread

    async def task(self, i):
        await asyncio.sleep(i)
        print(f'task {i} completed in {current_thread().getName()}')
        return i

    async def main(self):
        queue = asyncio.Queue()
        local_loop = asyncio.get_running_loop()

        def _on_done(future):
            print(f'{future} callback invoked in {current_thread().getName()}')
            local_loop.call_soon_threadsafe(
                lambda: print(f'call_soon in {current_thread().getName()}')
            )
            local_loop.call_soon_threadsafe(
                lambda: queue.put_nowait(future.result())
            )

        asyncio.create_task(self.task(1))
        asyncio.run_coroutine_threadsafe(
            self.task(2), self.async_thread.loop
        ).add_done_callback(_on_done)  # yapf: disable
        result = await queue.get()
        print(f'get result {result}')

        print('main thread exit')

    def run(self) -> None:
        asyncio.new_event_loop().run_until_complete(self.main())


async_thread = AsyncThread()
control_thread = ControlThread(async_thread)

async_thread.start()
control_thread.start()
