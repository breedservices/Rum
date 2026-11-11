.. currentmodule:: rum

API Reference
=============

The following section outlines the API of rum's prefixed command extension module.

.. note::

    Using prefixed commands in guilds requires :attr:`Intents.message_content` to be enabled.


.. _ext_commands_api_bot:

Bots
----

Bot
~~~

.. attributetable:: rum.ext.commands.Bot

.. autoclass:: rum.ext.commands.Bot
    :members:
    :inherited-members:
    :exclude-members: after_invoke, before_invoke, check, check_once, command, event, group, listen

    .. automethod:: Bot.after_invoke()
        :decorator:

    .. automethod:: Bot.before_invoke()
        :decorator:

    .. automethod:: Bot.check()
        :decorator:

    .. automethod:: Bot.check_once()
        :decorator:

    .. automethod:: Bot.command(*args, **kwargs)
        :decorator:

    .. automethod:: Bot.event()
        :decorator:

    .. automethod:: Bot.group(*args, **kwargs)
        :decorator:

    .. automethod:: Bot.listen(name=None, once=False)
        :decorator:

AutoShardedBot
~~~~~~~~~~~~~~

.. attributetable:: rum.ext.commands.AutoShardedBot

.. autoclass:: rum.ext.commands.AutoShardedBot
    :members:

Prefix Helpers
--------------

.. autofunction:: rum.ext.commands.when_mentioned

.. autofunction:: rum.ext.commands.when_mentioned_or

.. _ext_commands_api_events:

Event Reference
---------------

These events function similar to :ref:`the regular events <discord-api-events>`, except they
are custom to the command extension module.

.. function:: rum.ext.commands.on_command_error(ctx, error)

    An error handler that is called when an error is raised
    inside a command either through user input error, check
    failure, or an error in your own code.

    A default one is provided (:meth:`.Bot.on_command_error`).

    :param ctx: The invocation context.
    :type ctx: :class:`.Context`
    :param error: The error that was raised.
    :type error: :class:`.CommandError` derived

.. function:: rum.ext.commands.on_command(ctx)

    An event that is called when a command is found and is about to be invoked.

    This event is called regardless of whether the command itself succeeds via
    error or completes.

    :param ctx: The invocation context.
    :type ctx: :class:`.Context`

.. function:: rum.ext.commands.on_command_completion(ctx)

    An event that is called when a command has completed its invocation.

    This event is called only if the command succeeded, i.e. all checks have
    passed and the user input it correctly.

    :param ctx: The invocation context.
    :type ctx: :class:`.Context`

.. _ext_commands_api_command:

Commands
--------

Decorators
~~~~~~~~~~

.. autofunction:: rum.ext.commands.command
    :decorator:

.. autofunction:: rum.ext.commands.group
    :decorator:

Command
~~~~~~~

.. attributetable:: rum.ext.commands.Command

.. autoclass:: rum.ext.commands.Command
    :members:
    :special-members: __call__
    :exclude-members: after_invoke, before_invoke, error

    .. automethod:: Command.after_invoke()
        :decorator:

    .. automethod:: Command.before_invoke()
        :decorator:

    .. automethod:: Command.error()
        :decorator:

Group
~~~~~

.. attributetable:: rum.ext.commands.Group

.. autoclass:: rum.ext.commands.Group
    :members:
    :inherited-members:
    :exclude-members: after_invoke, before_invoke, command, error, group

    .. automethod:: Group.after_invoke()
        :decorator:

    .. automethod:: Group.before_invoke()
        :decorator:

    .. automethod:: Group.command(*args, **kwargs)
        :decorator:

    .. automethod:: Group.error()
        :decorator:

    .. automethod:: Group.group(*args, **kwargs)
        :decorator:

GroupMixin
~~~~~~~~~~

.. attributetable:: rum.ext.commands.GroupMixin

.. autoclass:: rum.ext.commands.GroupMixin
    :members:
    :exclude-members: command, group

    .. automethod:: GroupMixin.command(*args, **kwargs)
        :decorator:

    .. automethod:: GroupMixin.group(*args, **kwargs)
        :decorator:

.. _ext_commands_api_cogs:

Cogs
----

Cog
~~~

.. attributetable:: rum.ext.commands.Cog

.. autoclass:: rum.ext.commands.Cog
    :members:

CogMeta
~~~~~~~

.. attributetable:: rum.cog.CogMeta

.. autoclass:: rum.cog.CogMeta
    :members:

.. _ext_commands_help_command:

Help Commands
-------------

HelpCommand
~~~~~~~~~~~

.. attributetable:: rum.ext.commands.HelpCommand

.. autoclass:: rum.ext.commands.HelpCommand
    :members:

DefaultHelpCommand
~~~~~~~~~~~~~~~~~~

.. attributetable:: rum.ext.commands.DefaultHelpCommand

.. autoclass:: rum.ext.commands.DefaultHelpCommand
    :members:
    :exclude-members: send_bot_help, send_cog_help, send_group_help, send_command_help, prepare_help_command

MinimalHelpCommand
~~~~~~~~~~~~~~~~~~

.. attributetable:: rum.ext.commands.MinimalHelpCommand

.. autoclass:: rum.ext.commands.MinimalHelpCommand
    :members:
    :exclude-members: send_bot_help, send_cog_help, send_group_help, send_command_help, prepare_help_command

Paginator
~~~~~~~~~

.. attributetable:: rum.ext.commands.Paginator

.. autoclass:: rum.ext.commands.Paginator
    :members:

Enums
-----

.. class:: BucketType
    :module: rum.ext.commands

    Specifies a type of bucket for, e.g. a cooldown.

    .. attribute:: default

        The default bucket operates on a global basis.
    .. attribute:: user

        The user bucket operates on a per-user basis.
    .. attribute:: guild

        The guild bucket operates on a per-guild basis.
    .. attribute:: channel

        The channel bucket operates on a per-channel basis.
    .. attribute:: member

        The member bucket operates on a per-member basis.
    .. attribute:: category

        The category bucket operates on a per-category basis.
    .. attribute:: role

        The role bucket operates on a per-role basis.

        .. versionadded:: 1.3


.. _ext_commands_api_checks:

Checks
------

.. autofunction:: rum.ext.commands.check(predicate)
    :decorator:

.. autofunction:: rum.ext.commands.check_any(*checks)
    :decorator:

.. autofunction:: rum.ext.commands.has_role(item)
    :decorator:

.. autofunction:: rum.ext.commands.has_permissions(**perms)
    :decorator:

.. autofunction:: rum.ext.commands.has_guild_permissions(**perms)
    :decorator:

.. autofunction:: rum.ext.commands.has_any_role(*items)
    :decorator:

.. autofunction:: rum.ext.commands.bot_has_role(item)
    :decorator:

.. autofunction:: rum.ext.commands.bot_has_permissions(**perms)
    :decorator:

.. autofunction:: rum.ext.commands.bot_has_guild_permissions(**perms)
    :decorator:

.. autofunction:: rum.ext.commands.bot_has_any_role(*items)
    :decorator:

.. autofunction:: rum.ext.commands.cooldown(rate, per, type=rum.ext.commands.BucketType.default)
    :decorator:

.. autofunction:: rum.ext.commands.dynamic_cooldown(cooldown, type=BucketType.default)
    :decorator:

.. autofunction:: rum.ext.commands.max_concurrency(number, per=rum.ext.commands.BucketType.default, *, wait=False)
    :decorator:

.. autofunction:: rum.ext.commands.before_invoke(coro)
    :decorator:

.. autofunction:: rum.ext.commands.after_invoke(coro)
    :decorator:

.. autofunction:: rum.ext.commands.guild_only(,)
    :decorator:

.. autofunction:: rum.ext.commands.dm_only(,)
    :decorator:

.. autofunction:: rum.ext.commands.is_owner(,)
    :decorator:

.. autofunction:: rum.ext.commands.is_nsfw(,)
    :decorator:

.. _ext_commands_api_context:

Cooldown
--------

.. attributetable:: rum.ext.commands.Cooldown

.. autoclass:: rum.ext.commands.Cooldown
    :members:

Context
-------

.. attributetable:: rum.ext.commands.Context

.. autoclass:: rum.ext.commands.Context
    :members:
    :inherited-members:
    :exclude-members: history, typing

    .. automethod:: rum.ext.commands.Context.history
        :async-for:

    .. automethod:: rum.ext.commands.Context.typing
        :async-with:

.. _ext_commands_api_converters:

Converters
----------

.. autoclass:: rum.ext.commands.Converter
    :members:

.. autoclass:: rum.ext.commands.ObjectConverter
    :members:

.. autoclass:: rum.ext.commands.MemberConverter
    :members:

.. autoclass:: rum.ext.commands.UserConverter
    :members:

.. autoclass:: rum.ext.commands.MessageConverter
    :members:

.. autoclass:: rum.ext.commands.PartialMessageConverter
    :members:

.. autoclass:: rum.ext.commands.GuildChannelConverter
    :members:

.. autoclass:: rum.ext.commands.TextChannelConverter
    :members:

.. autoclass:: rum.ext.commands.VoiceChannelConverter
    :members:

.. autoclass:: rum.ext.commands.StageChannelConverter
    :members:

.. autoclass:: rum.ext.commands.CategoryChannelConverter
    :members:

.. autoclass:: rum.ext.commands.ForumChannelConverter
    :members:

.. autoclass:: rum.ext.commands.InviteConverter
    :members:

.. autoclass:: rum.ext.commands.GuildConverter
    :members:

.. autoclass:: rum.ext.commands.RoleConverter
    :members:

.. autoclass:: rum.ext.commands.GameConverter
    :members:

.. autoclass:: rum.ext.commands.ColourConverter
    :members:

.. autoclass:: rum.ext.commands.EmojiConverter
    :members:

.. autoclass:: rum.ext.commands.PartialEmojiConverter
    :members:

.. autoclass:: rum.ext.commands.ThreadConverter
    :members:

.. autoclass:: rum.ext.commands.GuildStickerConverter
    :members:

.. autoclass:: rum.ext.commands.clean_content
    :members:

.. autoclass:: rum.ext.commands.Greedy()

.. autofunction:: rum.ext.commands.run_converters

Flag Converter
~~~~~~~~~~~~~~

.. autoclass:: rum.ext.commands.FlagConverter
    :members:

.. autoclass:: rum.ext.commands.Flag()
    :members:

.. autofunction:: rum.ext.commands.flag

.. _ext_commands_api_errors:

Exceptions
----------

.. autoexception:: rum.ext.commands.CommandError
    :members:

.. autoexception:: rum.ext.commands.ConversionError
    :members:

.. autoexception:: rum.ext.commands.MissingRequiredArgument
    :members:

.. autoexception:: rum.ext.commands.ArgumentParsingError
    :members:

.. autoexception:: rum.ext.commands.UnexpectedQuoteError
    :members:

.. autoexception:: rum.ext.commands.InvalidEndOfQuotedStringError
    :members:

.. autoexception:: rum.ext.commands.ExpectedClosingQuoteError
    :members:

.. autoexception:: rum.ext.commands.BadArgument
    :members:

.. autoexception:: rum.ext.commands.BadUnionArgument
    :members:

.. autoexception:: rum.ext.commands.BadLiteralArgument
    :members:

.. autoexception:: rum.ext.commands.PrivateMessageOnly
    :members:

.. autoexception:: rum.ext.commands.NoPrivateMessage
    :members:

.. autoexception:: rum.ext.commands.CheckFailure
    :members:

.. autoexception:: rum.ext.commands.CheckAnyFailure
    :members:

.. autoexception:: rum.ext.commands.CommandNotFound
    :members:

.. autoexception:: rum.ext.commands.DisabledCommand
    :members:

.. autoexception:: rum.ext.commands.CommandInvokeError
    :members:

.. autoexception:: rum.ext.commands.TooManyArguments
    :members:

.. autoexception:: rum.ext.commands.UserInputError
    :members:

.. autoexception:: rum.ext.commands.CommandOnCooldown
    :members:

.. autoexception:: rum.ext.commands.MaxConcurrencyReached
    :members:

.. autoexception:: rum.ext.commands.NotOwner
    :members:

.. autoexception:: rum.ext.commands.MessageNotFound
    :members:

.. autoexception:: rum.ext.commands.MemberNotFound
    :members:

.. autoexception:: rum.ext.commands.GuildNotFound
    :members:

.. autoexception:: rum.ext.commands.UserNotFound
    :members:

.. autoexception:: rum.ext.commands.ChannelNotFound
    :members:

.. autoexception:: rum.ext.commands.ChannelNotReadable
    :members:

.. autoexception:: rum.ext.commands.ThreadNotFound
    :members:

.. autoexception:: rum.ext.commands.BadColourArgument
    :members:

.. autoexception:: rum.ext.commands.RoleNotFound
    :members:

.. autoexception:: rum.ext.commands.BadInviteArgument
    :members:

.. autoexception:: rum.ext.commands.EmojiNotFound
    :members:

.. autoexception:: rum.ext.commands.PartialEmojiConversionFailure
    :members:

.. autoexception:: rum.ext.commands.GuildStickerNotFound
    :members:

.. autoexception:: rum.ext.commands.BadBoolArgument
    :members:

.. autoexception:: rum.ext.commands.MissingPermissions
    :members:

.. autoexception:: rum.ext.commands.BotMissingPermissions
    :members:

.. autoexception:: rum.ext.commands.MissingRole
    :members:

.. autoexception:: rum.ext.commands.BotMissingRole
    :members:

.. autoexception:: rum.ext.commands.MissingAnyRole
    :members:

.. autoexception:: rum.ext.commands.BotMissingAnyRole
    :members:

.. autoexception:: rum.ext.commands.NSFWChannelRequired
    :members:

.. autoexception:: rum.ext.commands.FlagError
    :members:

.. autoexception:: rum.ext.commands.BadFlagArgument
    :members:

.. autoexception:: rum.ext.commands.MissingFlagArgument
    :members:

.. autoexception:: rum.ext.commands.TooManyFlags
    :members:

.. autoexception:: rum.ext.commands.MissingRequiredFlag
    :members:

.. autoexception:: rum.ext.commands.CommandRegistrationError
    :members:


Exception Hierarchy
~~~~~~~~~~~~~~~~~~~

.. exception_hierarchy::

    - :exc:`~.DiscordException`
        - :exc:`~.commands.CommandError`
            - :exc:`~.commands.ConversionError`
            - :exc:`~.commands.UserInputError`
                - :exc:`~.commands.MissingRequiredArgument`
                - :exc:`~.commands.TooManyArguments`
                - :exc:`~.commands.BadArgument`
                    - :exc:`~.commands.MessageNotFound`
                    - :exc:`~.commands.MemberNotFound`
                    - :exc:`~.commands.GuildNotFound`
                    - :exc:`~.commands.UserNotFound`
                    - :exc:`~.commands.ChannelNotFound`
                    - :exc:`~.commands.ChannelNotReadable`
                    - :exc:`~.commands.BadColourArgument`
                    - :exc:`~.commands.RoleNotFound`
                    - :exc:`~.commands.BadInviteArgument`
                    - :exc:`~.commands.EmojiNotFound`
                    - :exc:`~.commands.GuildStickerNotFound`
                    - :exc:`~.commands.PartialEmojiConversionFailure`
                    - :exc:`~.commands.BadBoolArgument`
                    - :exc:`~.commands.ThreadNotFound`
                    - :exc:`~.commands.FlagError`
                        - :exc:`~.commands.BadFlagArgument`
                        - :exc:`~.commands.MissingFlagArgument`
                        - :exc:`~.commands.TooManyFlags`
                        - :exc:`~.commands.MissingRequiredFlag`
                - :exc:`~.commands.BadUnionArgument`
                - :exc:`~.commands.BadLiteralArgument`
                - :exc:`~.commands.ArgumentParsingError`
                    - :exc:`~.commands.UnexpectedQuoteError`
                    - :exc:`~.commands.InvalidEndOfQuotedStringError`
                    - :exc:`~.commands.ExpectedClosingQuoteError`
            - :exc:`~.commands.CommandNotFound`
            - :exc:`~.commands.CheckFailure`
                - :exc:`~.commands.CheckAnyFailure`
                - :exc:`~.commands.PrivateMessageOnly`
                - :exc:`~.commands.NoPrivateMessage`
                - :exc:`~.commands.NotOwner`
                - :exc:`~.commands.MissingPermissions`
                - :exc:`~.commands.BotMissingPermissions`
                - :exc:`~.commands.MissingRole`
                - :exc:`~.commands.BotMissingRole`
                - :exc:`~.commands.MissingAnyRole`
                - :exc:`~.commands.BotMissingAnyRole`
                - :exc:`~.commands.NSFWChannelRequired`
            - :exc:`~.commands.DisabledCommand`
            - :exc:`~.commands.CommandInvokeError`
            - :exc:`~.commands.CommandOnCooldown`
            - :exc:`~.commands.MaxConcurrencyReached`
    - :exc:`~.ClientException`
        - :exc:`~.commands.CommandRegistrationError`
