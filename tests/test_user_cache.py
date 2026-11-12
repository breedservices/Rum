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
    payload = {
        "id": "2",
        "username": "someone",
        "discriminator": "1234",
        "avatar": None,
    }
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
    payload = {
        "id": "2",
        "username": "someone",
        "discriminator": "1234",
        "avatar": None,
    }
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
        "user": {
            "id": "2",
            "username": "someone",
            "discriminator": "0",
            "avatar": None,
        },
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
        "user": {
            "id": "2",
            "username": "someone",
            "discriminator": "0",
            "avatar": None,
        },
        "roles": ["10", "20"],
    }
    member = Member(guild=guild, data=payload, state=state)
    member._update(payload)
    other = Member(guild=guild, data=payload, state=state)
    assert member._roles is other._roles


GUILD_COUNT = 4
USERS_PER_GUILD = 60
ROLE_SETS = (["10"], ["10", "11"], ["12"], ["10", "12", "13"])


def _scale_state():
    events = []

    def dispatch(name, *args):
        events.append(name)

    state = ConnectionState(
        dispatch=dispatch,
        handlers={},
        hooks={},
        http=None,
        loop=None,
        intents=rum.Intents(members=True),
    )
    guilds = []
    for guild_index in range(GUILD_COUNT):
        guild = state._get_create_guild(
            {
                "id": str(100 + guild_index),
                "name": f"guild{guild_index}",
                "roles": [
                    {
                        "id": role_id,
                        "name": f"role{role_id}",
                        "permissions": "0",
                        "position": position,
                        "color": 0,
                        "hoist": False,
                        "managed": False,
                        "mentionable": False,
                        "colors": {
                            "primary_color": 0,
                            "secondary_color": 0,
                            "tertiary_color": 0,
                        },
                    }
                    for position, role_id in enumerate(("10", "11", "12", "13"))
                ],
                "channels": [],
                "members": [],
            }
        )
        state._get_guild(guild.id)
        guilds.append(guild)
    return state, guilds, events


def _member_payload(guild_id, user_id, roles):
    return {
        "guild_id": str(guild_id),
        "user": {
            "id": str(user_id),
            "username": f"user{user_id}",
            "discriminator": "0",
            "avatar": None,
        },
        "roles": roles,
        "joined_at": "2021-01-01T00:00:00.000000+00:00",
        "flags": 0,
    }


def test_cache_at_scale_across_guilds_and_updates():
    """The same users in many guilds share one user object, and the cache does
    not grow when the members are updated."""
    import tracemalloc

    state, guilds, events = _scale_state()

    tracemalloc.start()
    for guild in guilds:
        for user_index in range(USERS_PER_GUILD):
            state.parse_guild_member_add(
                _member_payload(
                    guild.id, user_index, ROLE_SETS[user_index % len(ROLE_SETS)]
                )
            )
    gc.collect()
    filled = tracemalloc.get_traced_memory()[0]

    # every user is one object, no matter how many guilds it is in
    assert len(state._users) == USERS_PER_GUILD
    for user_index in range(USERS_PER_GUILD):
        users = {guild.get_member(user_index)._user for guild in guilds}
        assert len(users) == 1

    # the members of a guild with the same roles share the role array
    guild = guilds[0]
    first = guild.get_member(0)
    other = guild.get_member(1)
    assert list(first._roles) != list(other._roles)
    assert first._roles is not other._roles
    same = [
        guild.get_member(index) for index in range(0, USERS_PER_GUILD, len(ROLE_SETS))
    ]
    assert all(member._roles is first._roles for member in same)

    # the roles of a member are the ones of its own guild
    for member_guild in guilds:
        for user_index in range(USERS_PER_GUILD):
            member = member_guild.get_member(user_index)
            assert list(member._roles) == [
                int(role_id) for role_id in ROLE_SETS[user_index % len(ROLE_SETS)]
            ]

    # updates keep the roles of the member and share the arrays again
    for guild in guilds:
        for user_index in range(USERS_PER_GUILD):
            state.parse_guild_member_update(
                _member_payload(guild.id, user_index, ["11", "13"])
            )
    gc.collect()
    updated = tracemalloc.get_traced_memory()[0]

    assert len(state._users) == USERS_PER_GUILD
    assert events.count("member_join") == GUILD_COUNT * USERS_PER_GUILD
    assert events.count("member_update") == GUILD_COUNT * USERS_PER_GUILD
    for guild in guilds:
        for user_index in range(USERS_PER_GUILD):
            member = guild.get_member(user_index)
            assert list(member._roles) == [11, 13]

    # the members leave and come back, which makes a new member object for a
    # user that is cached already
    for guild in guilds:
        for user_index in range(USERS_PER_GUILD):
            state.parse_guild_member_remove(_member_payload(guild.id, user_index, []))
            state.parse_guild_member_add(
                _member_payload(
                    guild.id, user_index, ROLE_SETS[user_index % len(ROLE_SETS)]
                )
            )
    gc.collect()
    rejoined = tracemalloc.get_traced_memory()[0]
    tracemalloc.stop()

    assert len(state._users) == USERS_PER_GUILD
    assert events.count("member_remove") == GUILD_COUNT * USERS_PER_GUILD
    for guild in guilds:
        for user_index in range(USERS_PER_GUILD):
            member = guild.get_member(user_index)
            assert list(member._roles) == [
                int(role_id) for role_id in ROLE_SETS[user_index % len(ROLE_SETS)]
            ]
            assert member._user is state._users[user_index]

    # the cache does not grow when the members come back
    assert rejoined < updated * 1.3, f"{rejoined} against {updated}"

    # the cache does not grow when the members are updated
    assert updated < filled * 1.1, f"{updated} against {filled}"
