:orphan:

.. currentmodule:: rum

.. _intro:

Installing rum
=================

This is the documentation for rum, a library for Python to aid
in creating applications that utilise the Discord API.

Prerequisites
-------------

rum works with Python 3.11 or higher. Support for earlier versions of Python
is not provided. Python 2.7 or lower is not supported. Python 3.8 or lower is not supported.


.. _installing:

Installing
----------

.. note::

    rum is not published on PyPI. Install it directly from the repository URL. ::

        python3 -m pip install -U "git+https://github.com/breedservices/Rum.git"

    For Windows users, this command should be used to install the pre-release: ::

        py -3 -m pip install -U "git+https://github.com/breedservices/Rum.git"

You can get the library directly from the repository: ::

    python3 -m pip install -U "git+https://github.com/breedservices/Rum.git"

If you are using Windows, then the following should be used instead: ::

    py -3 -m pip install -U "git+https://github.com/breedservices/Rum.git"


To install additional packages for speedup,  you should use ``rum[speed]`` instead of ``rum``, e.g.

.. code:: sh

    # Linux/macOS
    python3 -m pip install -U "rum[speed] @ git+https://github.com/breedservices/Rum.git"

    # Windows
    py -3 -m pip install -U "rum[speed] @ git+https://github.com/breedservices/Rum.git"


To get voice support, you should use ``rum[voice]`` instead of ``rum``, e.g. ::

    python3 -m pip install -U "rum[voice] @ git+https://github.com/breedservices/Rum.git"

On Linux environments, installing voice requires getting the following dependencies:

- `libffi <https://github.com/libffi/libffi>`_
- `libnacl <https://github.com/saltstack/libnacl>`_
- `python3-dev <https://packages.debian.org/python3-dev>`_

For a Debian-based system, the following command will get these dependencies:

.. code-block:: shell

    $ apt install libffi-dev libnacl-dev python3-dev

Remember to check your permissions!

Virtual Environments
~~~~~~~~~~~~~~~~~~~~

Sometimes you want to keep libraries from polluting system installs or use a different version of
libraries than the ones installed on the system. You might also not have permissions to install libraries system-wide.
For this purpose, the standard library as of Python 3.3 comes with a concept called "Virtual Environment"s to
help maintain these separate versions.

A more in-depth tutorial is found on :doc:`py:tutorial/venv`.

However, for the quick and dirty:

1. Go to your project's working directory:

    .. code-block:: shell

        $ cd your-bot-source
        $ python3 -m venv bot-env

2. Activate the virtual environment:

    .. code-block:: shell

        $ source bot-env/bin/activate

    On Windows you activate it with:

    .. code-block:: shell

        $ bot-env\Scripts\activate.bat

3. Use pip like usual:

    .. code-block:: shell

        $ pip install -U "git+https://github.com/breedservices/Rum.git"

Congratulations. You now have a virtual environment all set up.

Installing from a Source Checkout
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To work on rum itself, clone the repository and install it in editable mode::

    $ git clone git@github.com:breedservices/Rum.git
    $ cd Rum
    $ pip install -e ".[voice]"

.. note::

    The extras must be quoted. Without the quotes the shell expands ``[voice]``
    as a glob pattern and the command fails with
    ``zsh: no matches found: [voice]``.

Alternatively, use `uv <https://docs.astral.sh/uv/>`_ which handles extras
without any quoting::

    $ uv sync --group dev --group test --extra voice

Basic Concepts
--------------

rum revolves around the concept of :ref:`events <discord-api-events>`.
An event is something you listen to and then respond to. For example, when a message
happens, you will receive an event about it that you can respond to.

A quick example to showcase how events work:

.. code-block:: python3

    import rum

    class MyClient(rum.Client):
        async def on_ready(self):
            print(f'Logged on as {self.user}!')

        async def on_message(self, message):
            print(f'Message from {message.author}: {message.content}')

    client = MyClient()
    client.run('my token goes here')
