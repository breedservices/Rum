"""
The MIT License (MIT)

Copyright (c) 2021-2026 Pycord Development

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

import io
import subprocess

from .core import CREATE_NO_WINDOW, Filters, Sink, default_filters
from .errors import MKASinkError


FFMPEG_TIMEOUT = 30


class MKASink(Sink):
    """A special sink for .mka files.

    .. versionadded:: 2.0
    """

    def __init__(self, *, filters=None):
        if filters is None:
            filters = default_filters
        self.filters = filters
        Filters.__init__(self, **self.filters)

        self.encoding = "mka"
        self.vc = None
        self.audio_data = {}

    def format_audio(self, audio):
        """Formats the recorded audio.

        Raises
        ------
        MKASinkError
            Audio may only be formatted after recording is finished.
        MKASinkError
            Formatting the audio failed.
        """
        vc = getattr(self, "vc", None)
        if vc is not None and vc.is_recording():
            raise MKASinkError(
                "Audio may only be formatted after recording is finished."
            )
        args = [
            "ffmpeg",
            "-f",
            "s16le",
            "-ar",
            "48000",
            "-loglevel",
            "error",
            "-ac",
            "2",
            "-i",
            "-",
            "-f",
            "matroska",
            "pipe:1",
        ]
        try:
            process = subprocess.Popen(
                args,
                creationflags=CREATE_NO_WINDOW,
                stdout=subprocess.PIPE,
                stdin=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
        except FileNotFoundError:
            raise MKASinkError("ffmpeg was not found.") from None
        except subprocess.SubprocessError as exc:
            raise MKASinkError(
                "Popen failed: {0.__class__.__name__}: {0}".format(exc)
            ) from exc

        try:
            out, err = process.communicate(audio.file.read(), timeout=FFMPEG_TIMEOUT)
        except subprocess.TimeoutExpired:
            process.kill()
            process.communicate()
            raise MKASinkError("ffmpeg timed out while formatting audio.") from None

        if process.returncode != 0:
            stderr = (err or b"").decode(errors="replace").strip()
            msg = "ffmpeg failed while formatting audio."
            if stderr:
                msg = f"{msg} {stderr}"
            raise MKASinkError(msg)

        out = io.BytesIO(out)
        out.seek(0)
        audio.file = out
        audio.on_format(self.encoding)
