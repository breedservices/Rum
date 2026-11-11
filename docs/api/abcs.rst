.. _discord_api_abcs:

Abstract Base Classes
=====================

An :term:`abstract base class` (also known as an ``abc``) is a class that models can inherit
to get their behaviour. **Abstract base classes should not be instantiated**.
They are mainly there for usage with :func:`isinstance` and :func:`issubclass`\.

This library has a module related to abstract base classes, in which all the ABCs are subclasses of
:class:`typing.Protocol`.

.. attributetable:: rum.abc.Snowflake

.. autoclass:: rum.abc.Snowflake()
    :members:

.. attributetable:: rum.abc.User

.. autoclass:: rum.abc.User()
    :members:

.. attributetable:: rum.abc.PrivateChannel

.. autoclass:: rum.abc.PrivateChannel()
    :members:

.. attributetable:: rum.abc.GuildChannel

.. autoclass:: rum.abc.GuildChannel()
    :members:

.. attributetable:: rum.abc.Messageable

.. autoclass:: rum.abc.Messageable()
    :members:
    :exclude-members: history, typing

    .. automethod:: rum.abc.Messageable.history
        :async-for:

    .. automethod:: rum.abc.Messageable.typing
        :async-with:

.. attributetable:: rum.abc.Connectable

.. autoclass:: rum.abc.Connectable()
