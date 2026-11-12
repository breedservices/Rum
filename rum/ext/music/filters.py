from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .enums import FadeCurve

__all__ = (
    "AudioFading",
    "ChannelMix",
    "Chorus",
    "Compressor",
    "Distortion",
    "Echo",
    "Equalizer",
    "Filter",
    "Filters",
    "HighPass",
    "Karaoke",
    "LowPass",
    "Phaser",
    "Rotation",
    "Spatial",
    "Timescale",
    "Tremolo",
    "Vibrato",
    "Volume",
)


class Filter:
    """Base filter that serializes to a Lavalink/NodeLink filter payload."""

    __slots__ = ()

    def to_dict(self) -> dict[str, Any]:
        """Return the filter's JSON-serializable payload fragment."""
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


@dataclass(slots=True)
class HighPass(Filter):
    smoothing: float | None = None

    def to_dict(self) -> dict[str, Any]:
        return (
            {"highpass": {"smoothing": self.smoothing}}
            if self.smoothing is not None
            else {}
        )


@dataclass(slots=True)
class Echo(Filter):
    delay: float | None = None
    feedback: float | None = None
    mix: float | None = None

    def to_dict(self) -> dict[str, Any]:
        payload = {
            k: v
            for k, v in {
                "delay": self.delay,
                "feedback": self.feedback,
                "mix": self.mix,
            }.items()
            if v is not None
        }
        return {"echo": payload} if payload else {}


@dataclass(slots=True)
class Chorus(Filter):
    rate: float | None = None
    depth: float | None = None
    delay: float | None = None
    mix: float | None = None
    feedback: float | None = None

    def to_dict(self) -> dict[str, Any]:
        payload = {
            k: v
            for k, v in {
                "rate": self.rate,
                "depth": self.depth,
                "delay": self.delay,
                "mix": self.mix,
                "feedback": self.feedback,
            }.items()
            if v is not None
        }
        return {"chorus": payload} if payload else {}


@dataclass(slots=True)
class Compressor(Filter):
    threshold: float | None = None
    ratio: float | None = None
    attack: float | None = None
    release: float | None = None
    gain: float | None = None

    def to_dict(self) -> dict[str, Any]:
        payload = {
            k: v
            for k, v in {
                "threshold": self.threshold,
                "ratio": self.ratio,
                "attack": self.attack,
                "release": self.release,
                "gain": self.gain,
            }.items()
            if v is not None
        }
        return {"compressor": payload} if payload else {}


@dataclass(slots=True)
class Phaser(Filter):
    stages: int | None = None
    rate: float | None = None
    depth: float | None = None
    feedback: float | None = None
    mix: float | None = None
    min_frequency: float | None = None
    max_frequency: float | None = None

    def to_dict(self) -> dict[str, Any]:
        payload = {
            k: v
            for k, v in {
                "stages": self.stages,
                "rate": self.rate,
                "depth": self.depth,
                "feedback": self.feedback,
                "mix": self.mix,
                "minFrequency": self.min_frequency,
                "maxFrequency": self.max_frequency,
            }.items()
            if v is not None
        }
        return {"phaser": payload} if payload else {}


@dataclass(slots=True)
class Spatial(Filter):
    depth: float | None = None
    rate: float | None = None

    def to_dict(self) -> dict[str, Any]:
        payload = {
            k: v
            for k, v in {"depth": self.depth, "rate": self.rate}.items()
            if v is not None
        }
        return {"spatial": payload} if payload else {}


@dataclass(slots=True)
class AudioFading:
    enabled: bool | None = None
    track_start: dict[str, Any] | None = None
    track_end: dict[str, Any] | None = None
    track_stop: dict[str, Any] | None = None
    seek: dict[str, Any] | None = None
    ducking: dict[str, Any] | None = None

    @staticmethod
    def step(
        duration: int, curve: FadeCurve | str = FadeCurve.LINEAR
    ) -> dict[str, Any]:
        c = curve.value if isinstance(curve, FadeCurve) else str(curve)
        return {"duration": int(duration), "curve": c}

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {}
        if self.enabled is not None:
            payload["enabled"] = self.enabled
        for key, value in (
            ("trackStart", self.track_start),
            ("trackEnd", self.track_end),
            ("trackStop", self.track_stop),
            ("seek", self.seek),
            ("ducking", self.ducking),
        ):
            if value:
                payload[key] = value
        return payload


class Filters:
    """Collection of audio filters applied to a player."""

    __slots__ = ("_filters",)

    def __init__(self) -> None:
        """Create an empty filter set."""
        self._filters: dict[str, Filter] = {}

    def add(self, f: Filter) -> Filters:
        """Add or replace a filter of the given type."""
        self._filters[type(f).__name__.lower()] = f
        return self

    set = add

    def remove(self, filter_type: type[Filter]) -> Filters:
        """Remove a filter type if present."""
        self._filters.pop(filter_type.__name__.lower(), None)
        return self

    def clear(self) -> None:
        """Remove all filters."""
        self._filters.clear()

    def to_dict(self) -> dict[str, Any]:
        """Serialize all filters into a single payload dict."""
        payload: dict[str, Any] = {}
        for f in self._filters.values():
            payload.update(f.to_dict())
        return payload
