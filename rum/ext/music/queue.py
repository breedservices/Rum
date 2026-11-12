from __future__ import annotations

import random
from collections import deque
from collections.abc import Iterable, Iterator

from .exceptions import QueueEmpty
from .objects import Track

__all__ = ("Queue",)


class Queue:
    """Default in-memory track queue for :class:`~rum.ext.music.Player`.

    A custom queue provider can be used instead by passing a compatible object to
    ``Player(..., queue=...)``. At minimum, a player expects ``loop_mode`` (``None``,
    ``"track"``, or ``"queue"``) and ``get() -> Track`` that raises
    :class:`~rum.ext.music.QueueEmpty` when no track is available.
    """

    __slots__ = ("_history", "_queue", "loop_mode", "max_size")

    def __init__(self, *, max_size: int | None = None) -> None:
        """Create a queue.

        Parameters
        ----------
        max_size:
            Optional maximum number of queued (upcoming) tracks.
        """
        self._queue: deque[Track] = deque()
        self._history: deque[Track] = deque()
        self.max_size = max_size
        self.loop_mode: str | None = None  # "track", "queue", or None

    def __len__(self) -> int:
        """Return the number of upcoming tracks."""
        return len(self._queue)

    def __iter__(self) -> Iterator[Track]:
        """Iterate over upcoming tracks without removing them."""
        return iter(self._queue)

    def __bool__(self) -> bool:
        """Return ``True`` if there are upcoming tracks."""
        return bool(self._queue)

    @property
    def is_empty(self) -> bool:
        """Whether the queue has no upcoming tracks."""
        return not self._queue

    @property
    def is_full(self) -> bool:
        """Whether the queue reached ``max_size``."""
        m = self.max_size
        return m is not None and len(self._queue) >= m

    @property
    def count(self) -> int:
        """Alias for the number of upcoming tracks."""
        return len(self._queue)

    @property
    def history(self) -> list[Track]:
        """A snapshot list of tracks previously returned by :meth:`get`."""
        return list(self._history)

    def clear(self) -> None:
        """Remove all upcoming tracks."""
        self._queue.clear()

    def clear_history(self) -> None:
        """Remove all recorded history entries."""
        self._history.clear()

    def add(self, track: Track) -> None:
        """Append a track to the queue."""
        if self.is_full:
            raise QueueEmpty("Queue is full")
        self._queue.append(track)

    put = add

    def extend(self, tracks: Iterable[Track]) -> None:
        """Append multiple tracks in order."""
        q = self._queue
        m = self.max_size
        for t in tracks:
            if m is not None and len(q) >= m:
                raise QueueEmpty("Queue is full")
            q.append(t)

    def get(self) -> Track:
        """Pop and return the next track.

        Records the track in history and, if ``loop_mode`` is ``"queue"``,
        appends it back to the end.
        """
        if not self._queue:
            raise QueueEmpty("Queue is empty")
        track = self._queue.popleft()
        self._history.append(track)
        if self.loop_mode == "queue":
            self._queue.append(track)
        return track

    def pop(self, index: int = 0) -> Track:
        """Remove and return a track by index (default: first)."""
        if not self._queue:
            raise QueueEmpty("Queue is empty")
        if index == 0:
            return self._queue.popleft()
        track = self._queue[index]
        del self._queue[index]
        return track

    def remove(self, track: Track) -> None:
        """Remove the first occurrence of a track."""
        self._queue.remove(track)

    def peek(self, index: int = 0) -> Track:
        """Return a track by index without removing it."""
        if not self._queue:
            raise QueueEmpty("Queue is empty")
        return self._queue[index]

    def shuffle(self) -> None:
        """Shuffle upcoming tracks in place."""
        items = list(self._queue)
        random.shuffle(items)
        self._queue = deque(items)

    def set_loop(self, mode: str | None) -> None:
        """Set loop mode to ``None``, ``"track"``, or ``"queue"``."""
        if mode not in (None, "track", "queue"):
            raise ValueError("loop mode must be None, 'track', or 'queue'")
        self.loop_mode = mode

    @property
    def upcoming(self) -> list[Track]:
        """A snapshot list of upcoming tracks."""
        return list(self._queue)
