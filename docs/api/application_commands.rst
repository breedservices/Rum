.. currentmodule:: rum

Application Commands
====================


Command Permission Decorators
-----------------------------

.. autofunction:: rum.commands.default_permissions
    :decorator:

.. autofunction:: rum.commands.guild_only
    :decorator:

.. autofunction:: rum.commands.is_nsfw
    :decorator:


Commands
--------

Shortcut Decorators
~~~~~~~~~~~~~~~~~~~

.. autofunction:: rum.commands.application_command
    :decorator:

.. autofunction:: rum.commands.command
    :decorator:

.. autofunction:: rum.commands.slash_command
    :decorator:

.. autofunction:: rum.commands.user_command
    :decorator:

.. autofunction:: rum.commands.message_command
    :decorator:

Objects
~~~~~~~

.. attributetable:: ApplicationCommand
.. autoclass:: ApplicationCommand
    :members:

.. attributetable:: SlashCommand
.. autoclass:: SlashCommand
    :members:
    :exclude-members: cog

.. attributetable:: SlashCommandGroup
.. autoclass:: SlashCommandGroup
    :members:

.. attributetable:: UserCommand
.. autoclass:: UserCommand
    :members:

.. attributetable:: MessageCommand
.. autoclass:: MessageCommand
    :members:

Options
-------

Shortcut Decorators
~~~~~~~~~~~~~~~~~~~
.. autofunction:: rum.commands.option
    :decorator:

Objects
~~~~~~~

.. attributetable:: Option
.. autoclass:: Option
    :members:

.. attributetable:: ThreadOption
.. autoclass:: ThreadOption
    :members:

.. attributetable:: OptionChoice
.. autoclass:: OptionChoice
    :members:


Context Objects
---------------

.. attributetable:: ApplicationContext
.. autoclass:: ApplicationContext
    :members:

.. attributetable:: AutocompleteContext
.. autoclass:: AutocompleteContext
    :members:
