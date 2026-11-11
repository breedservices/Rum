.. currentmodule:: rum

API Reference
=============

The reference manual that follows details the API of rum's bridge command extension module.

.. note::

    Using the prefixed command version (which uses the ``ext.commands`` extension) of bridge
    commands in guilds requires :attr:`Intents.message_context` to be enabled.


.. _ext_bridge_api:

Bots
----

Bot
~~~

.. attributetable:: rum.ext.bridge.Bot

.. autoclass:: rum.ext.bridge.Bot
    :members:

    .. automethod:: Bot.add_bridge_command()

    .. automethod:: Bot.bridge_command()
        :decorator:

    .. automethod:: Bot.bridge_group()
        :decorator:

AutoShardedBot
~~~~~~~~~~~~~~

.. attributetable:: rum.ext.bridge.AutoShardedBot

.. autoclass:: rum.ext.bridge.AutoShardedBot
    :members:

Event Reference
---------------

These events function similar to :ref:`the regular events <discord-api-events>`, except they
are custom to the bridge extension module.

.. function:: rum.ext.bridge.on_bridge_command_error(ctx, error)

    An error handler that is called when an error is raised
    inside a command either through user input error, check
    failure, or an error in your own code.

    :param ctx: The invocation context.
    :type ctx: :class:`.Context`
    :param error: The error that was raised.
    :type error: :class:`.CommandError` derived

.. function:: rum.ext.bridge.on_bridge_command(ctx)

    An event that is called when a command is found and is about to be invoked.

    This event is called regardless of whether the command itself succeeds via
    error or completes.

    :param ctx: The invocation context.
    :type ctx: :class:`.Context`

.. function:: rum.ext.bridge.on_bridge_command_completion(ctx)

    An event that is called when a command has completed its invocation.

    This event is called only if the command succeeded, i.e. all checks have
    passed and users input them correctly.

    :param ctx: The invocation context.
    :type ctx: :class:`.Context`

Commands
--------

BridgeCommand
~~~~~~~~~~~~~

.. attributetable:: rum.ext.bridge.BridgeCommand

.. autoclass:: rum.ext.bridge.BridgeCommand
    :members:

BridgeCommandGroup
~~~~~~~~~~~~~~~~~~

.. attributetable:: rum.ext.bridge.BridgeCommandGroup

.. autoclass:: rum.ext.bridge.BridgeCommandGroup
    :members:

Decorators
~~~~~~~~~~
.. automethod:: rum.ext.bridge.bridge_command()
    :decorator:

.. automethod:: rum.ext.bridge.bridge_group()
    :decorator:

.. automethod:: rum.ext.bridge.map_to()
    :decorator:

.. automethod:: rum.ext.bridge.guild_only()
    :decorator:

.. automethod:: rum.ext.bridge.is_nsfw()
    :decorator:

.. automethod:: rum.ext.bridge.has_permissions()
    :decorator:

Command Subclasses
~~~~~~~~~~~~~~~~~~

.. autoclass:: rum.ext.bridge.BridgeExtCommand

.. autoclass:: rum.ext.bridge.BridgeExtGroup

.. autoclass:: rum.ext.bridge.BridgeSlashCommand

.. autoclass:: rum.ext.bridge.BridgeSlashGroup

Context
-------

BridgeContext
~~~~~~~~~~~~~

.. attributetable:: rum.ext.bridge.BridgeContext

.. autoclass:: rum.ext.bridge.BridgeContext
    :members:
    :exclude-members: _respond, _defer, _edit, _get_super

BridgeContext Subclasses
~~~~~~~~~~~~~~~~~~~~~~~~

.. attributetable:: rum.ext.bridge.BridgeApplicationContext

.. autoclass:: rum.ext.bridge.BridgeApplicationContext
    :members:

.. attributetable:: rum.ext.bridge.BridgeExtContext

.. autoclass:: rum.ext.bridge.BridgeExtContext
    :members:

.. attributetable:: rum.ext.bridge.Context

.. autoclass:: rum.ext.bridge.Context

    Alias of :data:`typing.Union` [ :class:`.BridgeExtContext`, :class:`.BridgeApplicationContext` ] for typing convenience.

Options
-------

Shortcut Decorators
~~~~~~~~~~~~~~~~~~~
.. autofunction:: rum.ext.bridge.bridge_option
    :decorator:

Objects
~~~~~~~

.. attributetable:: rum.ext.bridge.BridgeOption

.. autoclass:: rum.ext.bridge.BridgeOption
    :members:
