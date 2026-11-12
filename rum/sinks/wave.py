"""
The MIT License (MIT)

Copyright (c) 2015-2021 Rapptz
Copyright (c) 2021-2026 Pycord Development
Copyright (c) 2026-present The rum team

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""

import wave

from .core import Filters, Sink, default_filters
from .errors import WaveSinkError


class WaveSink(Sink):
    """A special sink for .wav(wave) files.

    .. versionadded:: 2.0
    """

    def __init__(self, *, filters=None):
        if filters is None:
            filters = default_filters
        self.filters = filters
        Filters.__init__(self, **self.filters)

        self.encoding = "wav"
        self.vc = None
        self.audio_data = {}

    def format_audio(self, audio):
        """Formats the recorded audio.

        Raises
        ------
        WaveSinkError
            Audio may only be formatted after recording is finished.
        WaveSinkError
            Formatting the audio failed.
        """
        vc = getattr(self, "vc", None)
        if vc is not None and vc.is_recording():
            raise WaveSinkError(
                "Audio may only be formatted after recording is finished."
            )

        from ..opus import Decoder

        channels = getattr(getattr(vc, "decoder", None), "CHANNELS", Decoder.CHANNELS)
        sample_size = getattr(
            getattr(vc, "decoder", None), "SAMPLE_SIZE", Decoder.SAMPLE_SIZE
        )
        sampling_rate = getattr(
            getattr(vc, "decoder", None), "SAMPLING_RATE", Decoder.SAMPLING_RATE
        )

        data = audio.file
        data.seek(0)
        pcm = data.read()

        data.seek(0)
        data.truncate(0)
        with wave.open(data, "wb") as f:
            f.setnchannels(channels)
            f.setsampwidth(sample_size // channels)
            f.setframerate(sampling_rate)
            f.writeframes(pcm)

        data.seek(0)
        audio.on_format(self.encoding)
