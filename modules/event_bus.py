import threading
from typing import Callable, Dict, List, Any


class EventBus:
    """
    Thread-safe event bus for decoupling core tracker and extension modules.
    Allows modules to communicate without hard dependencies.
    """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(EventBus, cls).__new__(cls)
                cls._instance._subscribers: Dict[str, List[Callable]] = {}
                cls._instance._sub_lock = threading.Lock()
            return cls._instance

    def subscribe(self, event_name: str, handler: Callable[..., Any]) -> None:
        """Register an event listener."""
        with self._sub_lock:
            if event_name not in self._subscribers:
                self._subscribers[event_name] = []
            if handler not in self._subscribers[event_name]:
                self._subscribers[event_name].append(handler)

    def unsubscribe(self, event_name: str, handler: Callable[..., Any]) -> None:
        """Remove an event listener."""
        with self._sub_lock:
            if event_name in self._subscribers and handler in self._subscribers[event_name]:
                self._subscribers[event_name].remove(handler)

    def emit(self, event_name: str, **kwargs: Any) -> None:
        """Broadcast an event to all registered listeners safely."""
        handlers = []
        with self._sub_lock:
            if event_name in self._subscribers:
                handlers = list(self._subscribers[event_name])

        for handler in handlers:
            try:
                handler(**kwargs)
            except Exception as exc:
                print(f"[EventBus] Error in handler for '{event_name}': {exc}")


event_bus = EventBus()

if __name__ == "__main__":
    print("=" * 60)
    print("🛰️  NEKO Tracker — EventBus Self-Test")
    print("=" * 60)
    test_results = []

    def on_test(amount=0, **kw):
        test_results.append(amount)
        print(f" [✓] Event received callback: amount={amount}")

    event_bus.subscribe("test_event", on_test)
    event_bus.emit("test_event", amount=500000)
    assert test_results == [500000], "Event delivery failed"
    print(" [✓] EventBus is functioning 100% properly!")
    print("=" * 60)
