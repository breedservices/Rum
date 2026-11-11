.. _discord_ui_kit:

Bot UI Kit
==========

The library has helpers to help create component-based UIs.


Shortcut decorators
-------------------

.. autofunction:: rum.ui.button
    :decorator:

.. autofunction:: rum.ui.select
    :decorator:

.. autofunction:: rum.ui.string_select
    :decorator:

.. autofunction:: rum.ui.user_select
    :decorator:

.. autofunction:: rum.ui.role_select
    :decorator:

.. autofunction:: rum.ui.mentionable_select
    :decorator:

.. autofunction:: rum.ui.channel_select
    :decorator:

Objects
-------

.. attributetable:: rum.ui.BaseView

.. autoclass:: rum.ui.BaseView
    :members:

.. attributetable:: rum.ui.View

.. autoclass:: rum.ui.View
    :members:
    :inherited-members:

.. attributetable:: rum.ui.DesignerView

.. autoclass:: rum.ui.DesignerView
    :members:
    :inherited-members:

.. attributetable:: rum.ui.Item

.. autoclass:: rum.ui.Item
    :members:

.. attributetable:: rum.ui.ViewItem

.. autoclass:: rum.ui.ViewItem
    :members:
    :inherited-members:

.. attributetable:: rum.ui.ModalItem

.. autoclass:: rum.ui.ModalItem
    :members:
    :inherited-members:

.. attributetable:: rum.ui.ActionRow

.. autoclass:: rum.ui.ActionRow
    :members:
    :inherited-members:

.. attributetable:: rum.ui.Button

.. autoclass:: rum.ui.Button
    :members:
    :inherited-members:

.. attributetable:: rum.ui.Select

.. autoclass:: rum.ui.Select
    :members:
    :inherited-members:


.. class:: rum.ui.StringSelect

    An alias for :class:`Select` with ``select_type`` as :attr:`rum.ComponentType.string_select`.

.. class:: rum.ui.UserSelect

    An alias for :class:`Select` with ``select_type`` as :attr:`rum.ComponentType.user_select`.

.. class:: rum.ui.RoleSelect

    An alias for :class:`Select` with ``select_type`` as :attr:`rum.ComponentType.role_select`.

.. class:: rum.ui.MentionableSelect

    An alias for :class:`Select` with ``select_type`` as :attr:`rum.ComponentType.mentionable_select`.

.. class:: rum.ui.ChannelSelect

    An alias for :class:`Select` with ``select_type`` as :attr:`rum.ComponentType.channel_select`.

.. attributetable:: rum.ui.Section

.. autoclass:: rum.ui.Section
    :members:
    :inherited-members:

.. attributetable:: rum.ui.TextDisplay

.. autoclass:: rum.ui.TextDisplay
    :members:
    :inherited-members:

.. attributetable:: rum.ui.Thumbnail

.. autoclass:: rum.ui.Thumbnail
    :members:
    :inherited-members:

.. attributetable:: rum.ui.MediaGallery

.. autoclass:: rum.ui.MediaGallery
    :members:
    :inherited-members:

.. attributetable:: rum.ui.File

.. autoclass:: rum.ui.File
    :members:
    :inherited-members:

.. attributetable:: rum.ui.Separator

.. autoclass:: rum.ui.Separator
    :members:
    :inherited-members:

.. attributetable:: rum.ui.Container

.. autoclass:: rum.ui.Container
    :members:
    :inherited-members:

.. attributetable:: rum.ui.BaseModal

.. autoclass:: rum.ui.BaseModal
    :members:
    :inherited-members:

.. attributetable:: rum.ui.Modal

.. autoclass:: rum.ui.Modal
    :members:
    :inherited-members:

.. attributetable:: rum.ui.DesignerModal

.. autoclass:: rum.ui.DesignerModal
    :members:
    :inherited-members:

.. attributetable:: rum.ui.Label

.. autoclass:: rum.ui.Label
    :members:
    :inherited-members:

.. attributetable:: rum.ui.InputText

.. autoclass:: rum.ui.InputText
    :members:
    :inherited-members:

.. attributetable:: rum.ui.FileUpload

.. autoclass:: rum.ui.FileUpload
    :members:
    :inherited-members:

.. attributetable:: rum.ui.RadioGroup

.. autoclass:: rum.ui.RadioGroup
    :members:
    :inherited-members:

.. attributetable:: rum.ui.CheckboxGroup

.. autoclass:: rum.ui.CheckboxGroup
    :members:
    :inherited-members:

.. attributetable:: rum.ui.Checkbox

.. autoclass:: rum.ui.Checkbox
    :members:
    :inherited-members:
