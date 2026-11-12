from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

__all__ = (
    "ChannelMix",
    "Distortion",
    "Equalizer",
    "Filter",
    "Filters",
    "Karaoke",
    "LowPass",
    "Rotation",
    "Timescale",
    "Tremolo",
    "Vibrato",
    "Volume",
)


class Filter:
    __slots__ = ()

    def to_dict(self) -> dict[str, Any]:
        raise NotImplementedError


@dataclass(slots=True)
class Volume(Filter):
    volume: float = 1.0

    def to_dict(self) -> dict[str, Any]:
        return {"volume": self.volume}


@dataclass(slots=True)
class Equalizer(Filter):
    bands: list[tuple[int, float]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {"equalizer": [{"band": b, "gain": g} for b, g in self.bands]}


@dataclass(slots=True)
class Karaoke(Filter):
    level: float | None = None
    mono_level: float | None = None
    filter_band: float | None = None
    filter_width: float | None = None

    def to_dict(self) -> dict[str, Any]:
        payload = {
            k: v
            for k, v in {
                "level": self.level,
                "monoLevel": self.mono_level,
                "filterBand": self.filter_band,
                "filterWidth": self.filter_width,
            }.items()
            if v is not None
        }
        return {"karaoke": payload} if payload else {}


@dataclass(slots=True)
class Timescale(Filter):
    speed: float | None = None
    pitch: float | None = None
    rate: float | None = None

    def to_dict(self) -> dict[str, Any]:
        payload = {
            k: v
            for k, v in {
                "speed": self.speed,
                "pitch": self.pitch,
                "rate": self.rate,
            }.items()
            if v is not None
        }
        return {"timescale": payload} if payload else {}


@dataclass(slots=True)
class Tremolo(Filter):
    frequency: float | None = None
    depth: float | None = None

    def to_dict(self) -> dict[str, Any]:
        payload = {
            k: v
            for k, v in {"frequency": self.frequency, "depth": self.depth}.items()
            if v is not None
        }
        return {"tremolo": payload} if payload else {}


@dataclass(slots=True)
class Vibrato(Filter):
    frequency: float | None = None
    depth: float | None = None

    def to_dict(self) -> dict[str, Any]:
        payload = {
            k: v
            for k, v in {"frequency": self.frequency, "depth": self.depth}.items()
            if v is not None
        }
        return {"vibrato": payload} if payload else {}


@dataclass(slots=True)
class Rotation(Filter):
    rotation_hz: float | None = None

    def to_dict(self) -> dict[str, Any]:
        return (
            {"rotation": {"rotationHz": self.rotation_hz}}
            if self.rotation_hz is not None
            else {}
        )


@dataclass(slots=True)
class Distortion(Filter):
    sin_offset: float | None = None
    sin_scale: float | None = None
    cos_offset: float | None = None
    cos_scale: float | None = None
    tan_offset: float | None = None
    tan_scale: float | None = None
    offset: float | None = None
    scale: float | None = None

    def to_dict(self) -> dict[str, Any]:
        payload = {
            k: v
            for k, v in {
                "sinOffset": self.sin_offset,
                "sinScale": self.sin_scale,
                "cosOffset": self.cos_offset,
                "cosScale": self.cos_scale,
                "tanOffset": self.tan_offset,
                "tanScale": self.tan_scale,
                "offset": self.offset,
                "scale": self.scale,
            }.items()
            if v is not None
        }
        return {"distortion": payload} if payload else {}


@dataclass(slots=True)
class ChannelMix(Filter):
    left_to_left: float | None = None
    left_to_right: float | None = None
    right_to_left: float | None = None
    right_to_right: float | None = None

    def to_dict(self) -> dict[str, Any]:
        payload = {
            k: v
            for k, v in {
                "leftToLeft": self.left_to_left,
                "leftToRight": self.left_to_right,
                "rightToLeft": self.right_to_left,
                "rightToRight": self.right_to_right,
            }.items()
            if v is not None
        }
        return {"channelMix": payload} if payload else {}


@dataclass(slots=True)
class LowPass(Filter):
    smoothing: float | None = None

    def to_dict(self) -> dict[str, Any]:
        return (
            {"lowPass": {"smoothing": self.smoothing}}
            if self.smoothing is not None
            else {}
        )


class Filters:
    __slots__ = ("_filters",)

    def __init__(self) -> None:
        self._filters: dict[str, Filter] = {}

    def add(self, f: Filter) -> Filters:
        self._filters[type(f).__name__.lower()] = f
        return self

    set = add

    def remove(self, filter_type: type[Filter]) -> Filters:
        self._filters.pop(filter_type.__name__.lower(), None)
        return self

    def clear(self) -> None:
        self._filters.clear()

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {}
        for f in self._filters.values():
            payload.update(f.to_dict())
        return payload
