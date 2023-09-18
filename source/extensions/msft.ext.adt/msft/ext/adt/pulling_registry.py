from typing import Callable, cast, Union
import threading
import asyncio
import time
from .adt import ADT

class AdtPullingAction:
    def __init__(self, callback: Callable, delay: float = ADT().pulling_delay) -> None:
        self._callback = callback
        self._delay = delay
        self._stop_event = threading.Event()

    def _pulling_action(self):
        while not self.stopped():
            self._callback()
            time.sleep(self._delay)

    def start(self):
        # self._pulling_handler = threading.Thread(target=asyncio.run, args=(self._pulling_action,))
        self._pulling_handler = threading.Thread(target=self._pulling_action)
        self._pulling_handler.start()

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()

    def destroy(self):
        self.stop()

class AdtPullingRegistry:
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'):
            cls.instance = super(AdtPullingRegistry, cls).__new__(cls)
            cls._pulling_action_registry = {}
            ### A registry of `handler_id` and `callback` which will be triggered regularly, based on `delay` value
        return cls.instance


    def find_action_by_id(self, handler_id: str) -> Union[AdtPullingAction, None]:
        return self._pulling_action_registry.get(handler_id)

    def start_action(self, handler_id: str):
        handler = self.find_action_by_id(handler_id)
        if  handler != None:
            handler.start()

    def stop_action(self, handler_id: str):
        handler = self.find_action_by_id(handler_id)
        if  handler != None:
            handler.stop()

    def register_action(self, handler_id: str, callback: Callable, delay: float = ADT().pulling_delay ) -> AdtPullingAction:
        if self.find_action_by_id(handler_id) == None:
            self._pulling_action_registry[handler_id] = AdtPullingAction(callback, delay)
        else:
            Exception(f"Pulling action with id: {handler_id} already registered")
        pass

    def deregister_action(self, handler_id: str):
        if self.find_action_by_id(handler_id) != None:
            handler = cast(AdtPullingAction, self._pulling_action_registry.pop(handler_id))
            handler.destroy()

    def deregister_all_actions(self):
        keys_to_process = list(self._pulling_action_registry)
        for i in keys_to_process:
            self.deregister_action(i)