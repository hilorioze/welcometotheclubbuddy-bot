import asyncio
import logging
from collections.abc import Callable, Coroutine, Generator
from typing import Any

TaskType = Coroutine[Any, Any, Any] | Generator[Any, Any, Any]


def _cancel_tasks(to_cancel: set["asyncio.Task[Any]"], loop: asyncio.AbstractEventLoop) -> None:
    if not to_cancel:
        return

    for task in to_cancel:
        task.cancel()

    loop.run_until_complete(asyncio.gather(*to_cancel, return_exceptions=True))

    for task in to_cancel:
        if task.cancelled():
            continue
        if task.exception() is not None:
            loop.call_exception_handler(
                {
                    "message": "unhandled exception during asyncio.run() shutdown",
                    "exception": task.exception(),
                    "task": task,
                },
            )


class TaskManager:
    """Task Manager for running startup and shutdown tasks with an event loop."""

    def __init__(
        self,
        *,
        on_startup: list[TaskType] | None = None,
        on_shutdown: list[TaskType] | None = None,
        tasks: list[TaskType] | None = None,
        logger: logging.Logger | None = None,
    ) -> None:
        """Initializes a TaskManager instance.

        :param on_startup: List of coroutines to be executed during startup.
        :param on_shutdown: List of coroutines to be executed during shutdown.
        :param tasks: List of coroutines representing tasks to be executed in the event loop.
        :param logger: Custom logger object for logging messages.
        """
        self.on_startup: list[TaskType] = on_startup or []
        self.on_shutdown: list[TaskType] = on_shutdown or []
        self.tasks: list[TaskType] = tasks or []
        self.loop: asyncio.AbstractEventLoop = None  # type: ignore[assignment]
        self.logger = logger or logging.getLogger(__name__)

    def run(self, loop: asyncio.AbstractEventLoop | None = None) -> None:
        """Runs startup tasks and keeps the event loop running until all tasks are completed."""
        if not self.tasks:
            self.logger.warning("You ran the loop with 0 tasks. Is it ok?")

        self.loop = loop or asyncio.new_event_loop()

        for startup_task in self.on_startup:
            self.loop.run_until_complete(startup_task)

        for task in self.tasks:
            self.loop.create_task(task)

        tasks = asyncio.all_tasks(self.loop)
        try:
            while tasks:
                results = self.loop.run_until_complete(
                    asyncio.gather(*tasks, return_exceptions=True),
                )
                for result in results:
                    if not isinstance(result, Exception):
                        continue
                    self.logger.exception(result)
                tasks = asyncio.all_tasks(self.loop)
        except KeyboardInterrupt:
            self.logger.info("Caught keyboard interrupt. Shutting down...")
        finally:
            for shutdown_task in self.on_shutdown:
                self.loop.run_until_complete(shutdown_task)
            _cancel_tasks(asyncio.all_tasks(self.loop), self.loop)
            self.loop.run_until_complete(self.loop.shutdown_asyncgens())
            if self.loop.is_running():
                self.loop.close()
            self.logger.info("Task Manager stopped")

    def add_task(
        self,
        task: TaskType | Callable[..., TaskType],
    ) -> None:
        """Adds a task to be run in the event loop.

        :param task: Coroutine or coroutine function with zero arguments.
        """
        if asyncio.iscoroutinefunction(task):
            task = task()
        elif not asyncio.iscoroutine(task):
            error_msg = "Task should be a coroutine or coroutine function"
            raise TypeError(error_msg)

        if self.loop and self.loop.is_running():
            self.loop.create_task(task)
        self.tasks.append(task)

    def add_task_on_startup(
        self,
        task: TaskType | Callable[..., TaskType],
    ) -> None:
        if asyncio.iscoroutinefunction(task):
            task = task()
        elif not asyncio.iscoroutine(task):
            error_msg = "Task on startup should be a coroutine or coroutine function"
            raise TypeError(error_msg)

        self.on_startup.append(task)

    def add_task_on_shutdown(
        self,
        task: TaskType | Callable[..., TaskType],
    ) -> None:
        if asyncio.iscoroutinefunction(task):
            task = task()
        elif not asyncio.iscoroutine(task):
            error_msg = "Task on shutdown should be a coroutine or coroutine function"
            raise TypeError(error_msg)

        self.on_shutdown.append(task)
