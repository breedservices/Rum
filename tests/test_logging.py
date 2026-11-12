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

Tests for the logging helpers.
"""

import logging

from rum import utils


def test_setup_logging_defaults_to_root_logger():
    root = logging.getLogger()
    handler = logging.StreamHandler()
    previous_level = root.level
    previous_handlers = list(root.handlers)
    try:
        utils.setup_logging(handler=handler)
        assert handler in root.handlers
        assert root.level == logging.INFO
    finally:
        root.handlers = previous_handlers
        root.setLevel(previous_level)


def test_setup_logging_can_target_the_library_logger():
    library = logging.getLogger("rum")
    handler = logging.StreamHandler()
    previous_level = library.level
    previous_handlers = list(library.handlers)
    try:
        utils.setup_logging(handler=handler, level=logging.DEBUG, root=False)
        assert handler in library.handlers
        assert library.level == logging.DEBUG
        assert handler not in logging.getLogger().handlers
    finally:
        library.handlers = previous_handlers
        library.setLevel(previous_level)


def test_library_loggers_are_named_after_the_package():
    # The loggers are derived from the module name, so they are "rum.*" and
    # not "discord.*" even though the compatibility package exists.
    assert logging.getLogger("rum.client").name == "rum.client"
