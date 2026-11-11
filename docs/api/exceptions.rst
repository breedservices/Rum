.. currentmodule:: rum

Exceptions
==========

Exception Hierarchy
-------------------

.. exception_hierarchy::

    - :exc:`Exception`
        - :exc:`DiscordException`
            - :exc:`ClientException`
                - :exc:`InvalidData`
                - :exc:`InvalidArgument`
                - :exc:`LoginFailure`
                - :exc:`ConnectionClosed`
                - :exc:`PrivilegedIntentsRequired`
                - :exc:`InteractionResponded`
            - :exc:`NoMoreItems`
            - :exc:`GatewayNotFound`
            - :exc:`HTTPException`
                - :exc:`Forbidden`
                - :exc:`NotFound`
                - :exc:`DiscordServerError`
            - :exc:`ApplicationCommandError`
                - :exc:`CheckFailure`
                - :exc:`ApplicationCommandInvokeError`
            - :exc:`ExtensionError`
                - :exc:`ExtensionAlreadyLoaded`
                - :exc:`ExtensionNotLoaded`
                - :exc:`NoEntryPointError`
                - :exc:`ExtensionFailed`
                - :exc:`ExtensionNotFound`
            - :exc:`sinks.SinkException`
                - :exc:`sinks.RecordingException`
                - :exc:`sinks.WaveSinkError`
                - :exc:`sinks.MP3SinkError`
                - :exc:`sinks.MP4SinkError`
                - :exc:`sinks.M4ASinkError`
                - :exc:`sinks.MKVSinkError`
                - :exc:`sinks.MKASinkError`
                - :exc:`sinks.OGGSinkError`
            - :exc:`MissingVoiceDependenciesError`

Objects
-------

The following exceptions are thrown by the library.

.. autoexception:: DiscordException

.. autoexception:: ClientException

.. autoexception:: LoginFailure

.. autoexception:: NoMoreItems

.. autoexception:: HTTPException
    :members:

.. autoexception:: Forbidden

.. autoexception:: NotFound

.. autoexception:: DiscordServerError

.. autoexception:: InvalidData

.. autoexception:: InvalidArgument

.. autoexception:: GatewayNotFound

.. autoexception:: ConnectionClosed

.. autoexception:: PrivilegedIntentsRequired

.. autoexception:: InteractionResponded

.. autoexception:: rum.opus.OpusError

.. autoexception:: rum.opus.OpusNotLoaded

.. autoexception:: rum.ApplicationCommandError
    :members:

.. autoexception:: rum.CheckFailure
    :members:

.. autoexception:: rum.ApplicationCommandInvokeError
    :members:

.. autoexception:: rum.ExtensionError
    :members:

.. autoexception:: rum.ExtensionAlreadyLoaded
    :members:

.. autoexception:: rum.ExtensionNotLoaded
    :members:

.. autoexception:: rum.NoEntryPointError
    :members:

.. autoexception:: rum.ExtensionFailed
    :members:

.. autoexception:: rum.ExtensionNotFound
    :members:

.. autoexception:: rum.sinks.SinkException

.. autoexception:: rum.sinks.RecordingException

.. autoexception:: rum.sinks.WaveSinkError

.. autoexception:: rum.sinks.MP3SinkError

.. autoexception:: rum.sinks.MP4SinkError

.. autoexception:: rum.sinks.M4ASinkError

.. autoexception:: rum.sinks.MKVSinkError

.. autoexception:: rum.sinks.MKASinkError

.. autoexception:: rum.sinks.OGGSinkError

.. autoexception:: rum.MissingVoiceDependenciesError
