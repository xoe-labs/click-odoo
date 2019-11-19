# Changes

## 2.0.0 (2019-01-22)

  - refactor to click native facilities, where possible
  - replace `@env_options()` named parameters with `context_settings` on
    `click.Command()`
  - replace `@env_options` wrapper with custom Command class
  - add `default_overrides` command key to manage script-scoped
    parameter defaults (eg. adjust default for `log_level` or
    `rollback`)
  - Rename to dodoo
  - Add plugin facilities

## 1.1.1 (2018-11-01)

  - add `with_addons_path` option to `@dodoo.env_options` to control the
    presence of the `--addons-path` option. Defaults to False. Enabled
    for the CLI.

## 1.1.0 (2018-10-31)

  - add `environment_manager` to `@dodoo.env_options`, providing a hook
    on `odoo.api.Environment` creation.
  - add `--addons-path` option to the CLI.
  - add `database_must_exist` env option to `@dodoo.env_options` so
    scripts can behave how they please in case the database is absent.

## 1.0.4 (2018-10-07)

  - silence deprecation warning
  - adapt tests for Odoo 12

## 1.0.3 (2018-06-05)

  - clarify the behaviour of `@env_option` `with_database` and
    `database_required` parameters; in particular, when `with_database`
    and `database_required` are both set (the default), the `--database`
    option can be omitted as long as a database is declared in the Odoo
    configuration file.

## 1.0.2 (2018-06-01)

  - refactor the OdooEnvironment class: it is much cleaner when it
    leaves the global Odoo config alone, so we completely move
    responsibility to initialize the Odoo config to the CLI part.

## 1.0.1 (2018-05-27)

  - better error logging and handling: all exceptions occuring in
    scripts under dodoo.env\_options are logged and converted to
    ClickException so we are sure they are both in the log file and on
    the console (handled by click) for the user to see. The
    OdooEnvironment context manager does not do additional logging,
    leaving that responsibility to the caller.

## 1.0.0 (2018-05-20)

  - close db connections when releasing OdooEnvironment
  - expose dodoo.odoo\_bin (odoo or openerp-server depending on Odoo
    series). not documented yet, because it should ideally be a full
    path corresponding to the installed dodoo.odoo, and I'm not sure how
    best to detect it yet.

## 1.0.0b4 (2018-05-17)

  - minor documentation improvements
  - add the possibility to run script without `--database` (ie without
    env, but with a properly initialized Odoo library such as addons
    path)
  - be more resilient in case we can't obtain a context for the user

## 1.0.0b3 (2018-03-22)

  - dodoo now exports the odoo namespace: `from dodoo import odoo` is an
    alias for `import odoo` (\>9) or `import openerp as odoo` (\<=9)
  - add a `with_rollback` option to the `env_options` decorator, to
    control the presence of the rollback optio
