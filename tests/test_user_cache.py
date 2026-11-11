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
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

"""Tests for the user cache eviction behaviour."""

import gc

import rum
from rum.state import ConnectionState


def _make_state(provider=None) -> ConnectionState:
    return ConnectionState(
        dispatch=lambda *args, **kwargs: None,
        handlers={},
        hooks={},
        http=None,
        loop=None,
        intents=rum.Intents(members=True),
        cache_provider=provider,
    )


def test_default_provider_keeps_object_references():
    provider = rum.DefaultCacheProvider()
    assert provider.keeps_object_references is True


def test_in_memory_cache_keeps_the_user():
    state = _make_state()
    payload = {"id": "2", "username": "someone", "discriminator": "1234", "avatar": None}
    state.store_user(payload)
    assert len(state._users) == 1

    gc.collect()
    # The cache holds a reference to the user, so it is not evicted.
    assert len(state._users) == 1


def test_external_cache_is_not_evicted():
    class ExternalProvider(rum.DefaultCacheProvider):
        def __init__(self):
            super().__init__()
            self.keeps_object_references = False

    state = _make_state(ExternalProvider())
    payload = {"id": "2", "username": "someone", "discriminator": "1234", "avatar": None}
    state.store_user(payload)
    assert len(state._users) == 1

    gc.collect()
    # The cache does not hold on to the object, so the eviction has to be
    # skipped, otherwise the entry would be dropped straight away.
    assert len(state._users) == 1
