from aiogram.fsm.storage.base import BaseEventIsolation, BaseStorage
from aiogram.fsm.storage.memory import MemoryStorage, SimpleEventIsolation


def create_dispatcher_simple_events_isolation() -> BaseEventIsolation:
    events_isolation: BaseEventIsolation = SimpleEventIsolation()
    return events_isolation


def create_dispatcher_memory_storage() -> BaseStorage:
    storage: BaseStorage = MemoryStorage()
    return storage
