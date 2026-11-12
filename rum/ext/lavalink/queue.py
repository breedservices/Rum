from __future__ import annotations

import random
from collections import deque
from collections.abc import Iterable, Iterator

from .exceptions import QueueEmpty
from .objects import Track

__all__ = ("Queue",)


class Queue:
    __slots__ = ("_history", "_queue", "loop_mode", "max_size")

    def __init__(self, *, max_size: int | None = None) -> None:
        self._queue: deque[Track] = deque()
        self._history: deque[Track] = deque()
        self.max_size = max_size
        self.loop_mode: str | None = None  # "track", "queue", or None

    def __len__(self) -> int:
        return len(self._queue)

    def __iter__(self) -> Iterator[Track]:
        return iter(self._queue)

    def __bool__(self) -> bool:
        return bool(self._queue)

    @property
    def is_empty(self) -> bool:
        return not self._queue

    @property
    def is_full(self) -> bool:
        m = self.max_size
        return m is not None and len(self._queue) >= m

    @property
    def count(self) -> int:
        return len(self._queue)

    @property
    def history(self) -> list[Track]:
        return list(self._history)

    def clear(self) -> None:
        self._queue.clear()

    def clear_history(self) -> None:
        self._history.clear()

    def add(self, track: Track) -> None:
        if self.is_full:
            raise QueueEmpty("Queue is full")
        self._queue.append(track)

    put = add

    def extend(self, tracks: Iterable[Track]) -> None:
        q = self._queue
        m = self.max_size
        for t in tracks:
            if m is not None and len(q) >= m:
                raise QueueEmpty("Queue is full")
            q.append(t)

    def get(self) -> Track:
        if not self._queue:
            raise QueueEmpty("Queue is empty")
        track = self._queue.popleft()
        self._history.append(track)
        if self.loop_mode == "queue":
            self._queue.append(track)
        return track

    def pop(self, index: int = 0) -> Track:
        if not self._queue:
            raise QueueEmpty("Queue is empty")
        if index == 0:
            return self._queue.popleft()
        track = self._queue[index]
        del self._queue[index]
        return track

    def remove(self, track: Track) -> None:
        self._queue.remove(track)

    def peek(self, index: int = 0) -> Track:
        if not self._queue:
            raise QueueEmpty("Queue is empty")
        return self._queue[index]

    def shuffle(self) -> None:
        items = list(self._queue)
        random.shuffle(items)
        self._queue = deque(items)

    def set_loop(self, mode: str | None) -> None:
        if mode not in (None, "track", "queue"):
            raise ValueError("loop mode must be None, 'track', or 'queue'")
        self.loop_mode = mode

    @property
    def upcoming(self) -> list[Track]:
        return list(self._queue)
