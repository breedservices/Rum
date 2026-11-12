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

Tests for the user cache eviction behaviour.
"""

import gc

import rum
from rum.cache import LRUCache
from rum.member import Member
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


def test_lru_cache_drops_the_least_recently_used_entry():
    cache = LRUCache(2)
    cache["a"] = 1
    cache["b"] = 2
    cache["a"]
    cache["c"] = 3
    assert "b" not in cache
    assert "a" in cache
    assert len(cache) == 2


def test_provider_bounds_the_user_and_member_caches():
    provider = rum.DefaultCacheProvider(max_users=10, max_members=5)
    assert isinstance(provider.create_user_cache(), LRUCache)
    assert isinstance(provider.create_guild_member_cache(None), LRUCache)
    assert not isinstance(rum.DefaultCacheProvider().create_user_cache(), LRUCache)


def test_member_status_is_offline_without_a_presence():
    state = _make_state()
    guild = state._get_create_guild({"id": "1", "name": "guild"})
    member = Member(
        guild=guild,
        data={
            "user": {
                "id": "2",
                "username": "someone",
                "discriminator": "0",
                "avatar": None,
            },
            "roles": [],
        },
        state=state,
    )
    assert member.status is rum.Status.offline
    assert member.raw_status == "offline"
    assert not member.is_on_mobile()


def test_member_status_follows_a_presence():
    state = _make_state()
    guild = state._get_create_guild({"id": "1", "name": "guild"})
    member = Member(
        guild=guild,
        data={
            "user": {
                "id": "2",
                "username": "someone",
                "discriminator": "0",
                "avatar": None,
            },
            "roles": [],
        },
        state=state,
    )
    member._presence_update(
        {"activities": [], "status": "online", "client_status": {"desktop": "online"}},
        {"id": "2"},
    )
    assert member.status is rum.Status.online
    assert member.desktop_status is rum.Status.online
    assert member.mobile_status is rum.Status.offline


def test_cached_user_is_handed_out_when_the_data_is_the_same():
    state = _make_state()
    payload = {"id": "2", "username": "someone", "discriminator": "0", "avatar": None}
    first = state.store_user(payload)
    second = state.store_user(dict(payload))
    assert first is second
    assert len(state._users) == 1


def test_cached_user_is_copied_when_the_data_changed():
    state = _make_state()
    payload = {"id": "2", "username": "someone", "discriminator": "0", "avatar": None}
    cached = state.store_user(payload)
    updated = state.store_user({**payload, "username": "someone else"})
    assert updated is not cached
    assert updated.name == "someone else"
    # the cached user is never made older
    assert state._users[2].name == "someone"


def test_members_with_the_same_roles_share_the_role_array():
    state = _make_state()
    guild = state._get_create_guild({"id": "1", "name": "guild"})
    payload = {
        "user": {"id": "2", "username": "someone", "discriminator": "0", "avatar": None},
        "roles": ["10", "20"],
    }
    first = Member(guild=guild, data=payload, state=state)
    second = Member(guild=guild, data=payload, state=state)
    assert first._roles is second._roles
    assert list(first._roles) == [10, 20]


def test_a_member_update_shares_the_role_array_again():
    state = _make_state()
    guild = state._get_create_guild({"id": "1", "name": "guild"})
    payload = {
        "user": {"id": "2", "username": "someone", "discriminator": "0", "avatar": None},
        "roles": ["10", "20"],
    }
    member = Member(guild=guild, data=payload, state=state)
    member._update(payload)
    other = Member(guild=guild, data=payload, state=state)
    assert member._roles is other._roles
