from collections import deque
import math
from typing import Optional, Tuple


class CadenceAnalyzer:
    """
    Analyzes the statistical entropy and jitter (variance) of Meseta/Item drop intervals.
    Detects artificial bot cadence where drops arrive with unnaturally rigid periodicity.
    """

    def __init__(
        self,
        window_size: int = 15,
        min_sample_size: int = 10,
        min_stddev_threshold: float = 0.05,
    ):
        self.window_size = window_size
        self.min_sample_size = min_sample_size
        self.min_stddev_threshold = min_stddev_threshold

        self._last_event_time: Optional[float] = None
        self._intervals: deque[float] = deque(maxlen=window_size)

    def reset(self) -> None:
        self._last_event_time = None
        self._intervals.clear()

    def record_event(self, event_time: float) -> Optional[float]:
        """
        Records an event epoch timestamp and returns current interval std_dev if enough samples exist.
        """
        if self._last_event_time is not None:
            interval = event_time - self._last_event_time
            # Ignore simultaneous batch drops (interval == 0.0) from the same mob/encounter
            # and ignore huge pauses (> 60s) where player was AFK or traveling
            if 0.0 < interval <= 60.0:
                self._intervals.append(interval)

        self._last_event_time = event_time
        return self.get_standard_deviation()

    def get_standard_deviation(self) -> Optional[float]:
        """Calculates population standard deviation of recorded drop intervals."""
        n = len(self._intervals)
        if n < self.min_sample_size:
            return None

        mean = sum(self._intervals) / n
        variance = sum((x - mean) ** 2 for x in self._intervals) / n
        return math.sqrt(variance)

    def is_robotic_cadence(self) -> Tuple[bool, Optional[float]]:
        """
        Evaluates whether current interval variance is unnaturally low (robotic/simulator).
        Returns (is_robotic, current_stddev).
        """
        stddev = self.get_standard_deviation()
        if stddev is None:
            return False, None

        n = len(self._intervals)
        mean = sum(self._intervals) / n if n > 0 else 0.0
        # Rapid combat drops (mean <= 1.0s) have naturally low integer-second variance.
        # Only flag when drops are periodically spaced (mean > 1.0s) with unnaturally rigid zero jitter.
        if mean > 1.0 and stddev < self.min_stddev_threshold:
            return True, stddev

        return False, stddev
