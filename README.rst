dodoo
=====

.. image:: https://img.shields.io/badge/license-LGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/lgpl-3.0-standalone.html
   :alt: License: LGPL-3
.. image:: https://badge.fury.io/py/dodoo.svg
    :target: http://badge.fury.io/py/dodoo
.. image:: https://travis-ci.org/xoe-labs/dodoo.svg?branch=master
   :target: https://travis-ci.org/xoe-labs/dodoo
.. image:: https://codecov.io/gh/xoe-labs/dodoo/branch/master/graph/badge.svg
  :target: https://codecov.io/gh/xoe-labs/dodoo

``dodoo`` is a beautiful, robust and extensible Odoo server API extension suite
for DevOps. It is based on the excellent Click_ library.

.. contents::

Quick start
~~~~~~~~~~~

Install it in an environment where Odoo is installed,

  pip install dodoo


Custom scripts
~~~~~~~~~~~~~~

Assuming the following script named ``list-users.py``.

.. code:: python

   from __future__ import print_function

   for u in env['res.users'].search([]):
       print(u.login, u.name)

It can be run with::

  dodoo run -d dbname --log-level=error list-users.py

The second technique to create scripts looks like this. Assuming
the following script named ``list-users2.py``.

.. code:: python

  #!/usr/bin/env python
  from __future__ import print_function
  import click

  import dodoo

  CTX_SETTINGS = dict(
      default_map={'log_level': 'error'}
  )

  @click.command(cls=dodoo.CommandWithOdooEnv, context_settings=CTX_SETTINGS)
  @click.option('--say-hello', is_flag=True)
  def main(env, say_hello):
      if say_hello:
          click.echo("Hello!")
      for u in env['res.users'].search([]):
          print(u.login, u.name)


  if __name__ == '__main__':
      main()

It can be run like this::

  $ ./list-users2.py --help
  Usage: list-users2.py [OPTIONS]

  Options:
    -c, --config PATH    Specify the Odoo configuration file. Other ways to
                         provide it are with the ODOO_RC or OPENERP_SERVER
                         environment variables, or ~/.odoorc (Odoo >= 10) or
                         ~/.openerp_serverrc.
    -d, --database TEXT  Specify the database name. If present, this
                         parameter takes precedence over the database
                         provided in the Odoo configuration file.
    --log-level TEXT     Specify the logging level. Accepted values depend on
                         the Odoo version, and include debug, info, warn, error.
                         [default: error]
    --logfile PATH       Specify the log file.
    --rollback           Rollback the transaction even if the script
                         does not raise an exception. Note that if
                         the script itself commits, this option has no
                         effect, this is why it is not named dry run.
                         This option is implied when an interactive
                         console is started.
    --say-hello
    --help               Show this message and exit.

  $ ./list-users2.py --say-hello -d dbname
  Hello!
  admin Administrator
  ...

dodoo Plugins
~~~~~~~~~~~~~

For extending tha comfort of the dodoo API itself, you can write a plugin.
It's recommended to clone the plugin scaffolding_ repository to get started.

The plugin registration is done in ``setup.py`` like this:

.. code:: python

  from setuptools import setup

  setup(
      name='yourplugin',
      version='0.1',
      py_modules=['yourplugin'],
      install_requires=[
          'dodoo',
      ],
      entry_points='''
          [core_package.cli_plugins]
          cool_subcommand=yourscript.cli:cool_subcommand
          another_subcommand=yourscript.cli:another_subcommand
      ''',
  )

Aside from accessing dodoo options through ``ctx.obj`` implicitly, you can be
explicite by reusing dodoo options in the following way:

.. code:: python

  import click
  from dodoo import options, main


  @main.command()
  # Set the addons path options and make it mandatory, see options.py
  @options.addons_path_opt(True)
  def subcommand(addons_path):
      """I do something domain specific."""


Supported Odoo versions
~~~~~~~~~~~~~~~~~~~~~~~

Odoo version 8, 9, 10, 11 and 12 are supported.

An important design goal is to provide a consistent behaviour
across Odoo versions.

.. note::

  ``dodoo`` does not mandate any particular method of installing odoo.
  The only prerequisiste is that ``import odoo`` (>= 10) or ``import openerp``
  (< 10) must work.

Database transactions
~~~~~~~~~~~~~~~~~~~~~

By default ``dodoo`` commits the transaction for you, unless your script
raises an exception. This is so that you don't need to put explicit commits
in your scripts, which are therefore easier to compose in larger transactions
(provided they pass around the same env).

There is a ``--rollback`` option to force a rollback.

A rollback is always performed after an interactive session. If you need to
commit changes made before or during an interactive session, use ``env.cr.commit()``.

Logging
~~~~~~~

In version 8, Odoo logs to stdout by default. On other versions
it is stderr. ``dodoo`` attempts to use stderr for Odoo 8 too.

Logging is controlled by the usual Odoo logging options (``--log-level``,
``--logfile``) or the Odoo configuration file.

Command line interface (dodoo)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code::

  Usage: dodoo [OPTIONS] [SCRIPT] [SCRIPT_ARGS]...

    Execute a python script in an initialized Odoo environment. The script has
    access to a 'env' global variable which is an odoo.api.Environment
    initialized for the given database. If no script is provided, the script
    is read from stdin or an interactive console is started if stdin appears
    to be a terminal.

  Options:
    -c, --config FILE               Specify the Odoo configuration file. Other
                                    ways to provide it are with the ODOO_RC or
                                    OPENERP_SERVER environment variables, or
                                    ~/.odoorc (Odoo >= 10) or
                                    ~/.openerp_serverrc.
    --addons-path TEXT              Specify the addons path. If present, this
                                    parameter takes precedence over the addons
                                    path provided in the Odoo configuration
                                    file.
    -d, --database TEXT             Specify the database name. If present, this
                                    parameter takes precedence over the database
                                    provided in the Odoo configuration file.
    --log-level TEXT                Specify the logging level. Accepted values
                                    depend on the Odoo version, and include
                                    debug, info, warn, error.  [default: info]
    --logfile FILE                  Specify the log file.
    --rollback                      Rollback the transaction even if the script
                                    does not raise an exception. Note that if
                                    the script itself commits, this option has
                                    no effect. This is why it is not named dry
                                    run. This option is implied when an
                                    interactive console is started.
    -i, --interactive / --no-interactive
                                    Inspect interactively after running the
                                    script.
    --shell-interface TEXT          Preferred shell interface for interactive
                                    mode. Accepted values are ipython, ptpython,
                                    bpython, python. If not provided they are
                                    tried in this order.
    --help                          Show this message and exit.

Most options above are the same as ``odoo`` options and behave identically.
Additional Odoo options can be set in the the configuration file.
Note however that most server-related options (workers, http interface etc)
are ignored because no server is actually started when running a script.

An important feature of ``dodoo`` compared to, say, ``odoo shell`` is
the capability to pass arguments to scripts.

In order to avoid confusion between ``dodoo`` options and your script
options and arguments, it is recommended to separate them with ``--``::

  dodoo -d dbname -- list-users.py -d a b
  ./list-users.py -d dbname -- -d a b

In both examples above, ``sys.argv[1:]`` will contain ``['-d', 'a', 'b']``
in the script.

API
~~~

``env_options``
---------------

Customize the behaviour of ``dodoo.CommandWithOdooEnv`` through
``click.Command(env_options={})``.

``dodoo.CommandWithOdooEnv`` prepares an odoo ``Environment`` and passes
it as a ``env`` parameter.

It is configurable with the following keyword arguments in ``env_options``:

database_must_exist
  If this flag is False and the selected database does not exist
  do not fail and pass env=None instead (default: True).

environment_manager
  **experimental feature** A context manager that yields an intialized
  ``odoo.api.Environment``.
  It is invoked after Odoo configuration parsing and initialization.
  It must have the following signature (identical to ``OdooEnvironment``
  below, plus ``**kwargs``)

  .. code-block:: python

    environment_manager(database, rollback, **kwargs)


dodoo.odoo namespace
--------------------

As a convenience ``dodoo`` exports the ``odoo`` namespace, so
``from dodoo import odoo`` is an alias for ``import odoo`` (>9)
or ``import openerp as odoo`` (<=9).

OdooEnvironment context manager (experimental)
----------------------------------------------

This package also provides an experimental ``OdooEnvironment`` context manager.
It is meant to be used in after properly intializing Odoo (ie parsing the
configuration file etc).

.. warning::

   This API is considered experimental, contrarily to the scripting mechanism
   (ie passing ``env`` to scripts) and ``env_options`` decorator which are
   stable features. Should you have a specific usage for this API and would
   like it to become stable, get it touch to discuss your requirements.

Example:

.. code:: python

  from dodoo import OdooEnvironment


  with OdooEnvironment(database='dbname') as env:
      env['res.users'].search([])

Developement
~~~~~~~~~~~~

To run tests, type ``tox``. Tests are made using pytest. To run tests matching
a specific keyword for, say, Odoo 12 and python 3.6, use
``tox -e py36-12.0 -- -k keyword``.

This project uses `black <https://github.com/ambv/black>`_
as code formatting convention, as well as isort and flake8.
To make sure local coding convention are respected before
you commit, install
`pre-commit <https://github.com/pre-commit/pre-commit>`_ and
run ``pre-commit install`` after cloning the repository.

Useful links
~~~~~~~~~~~~

- pypi page: https://pypi.org/project/dodoo
- code repository: https://github.com/xoe-labs/dodoo
- report issues at: https://github.com/xoe-labs/dodoo/issues

.. _Click: http://click.pocoo.org
.. _scaffolding: https://github.com/coe-labs/dodoo-plugin-scaffold

Credits
~~~~~~~

Original Author:

- Stéphane Bidoul (`ACSONE <http://acsone.eu/>`_)

Contributor:

- David Arnold (`XOE <https://xoe.solutions>`_)

Maintainer:

- David Arnold (`XOE <https://xoe.solutions>`_)

Inspiration has been drawn from:

- `click-odoo by Acsone <https://github.com/acsone/click-odoo>`_
- `anybox.recipe.odoo <https://github.com/anybox/anybox.recipe.odoo>`_
- `anthem by Camptocamp <https://github.com/camptocamp/anthem>`_
- odoo's own shell command

Maintainer
~~~~~~~~~~

.. image:: https://erp.xoe.solutions/logo.png
   :alt: XOE Corp. SAS
   :target: https://xoe.solutions

This project is maintained by XOE Corp. SAS.
