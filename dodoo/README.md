# `dodoo` Base Component

## Abstract

`dodoo` is a CLI or library entrypoint to the dodoo server middleware for Odoo.

- `KF 1:` it hot-reloads config for DB, SMTP and the admin password.
- `KF 2:` it supports libpg dsn. (ej. for db server multiplexing)
- `KF 3:` set max connection per database.
- `KF 4:` dbfilter on odoo version and client project version.
- `KF 5:` mount registry (database) specific addon folders.
- `KF := Killer Feature`

**It provides:**

- A clean and well-defined interface to the Odoo namespace as `dodoo.odoo`
  package (`import dodoo.interfaces.odoo as odoo`).
- A clean and well-defined monkey patcher class to patch Odoo under the packages
  `dodoo.patchers` and `dodoo.patchers.odoo`. (`from dodoo.patchers import
  BasePatcher`)
- A clean and well-defined handle to the database and their schemata as
  `dodoo.connections` package. (`from dodoo.connections import OdooCursor,
  DodooCursor, PyblicCursor, SchemaCursor`).
- A clean and slick handle to the current repository puls Odoo specific helper
  mthods under the `dodoo.git` package (`from dodoo.git import Repo`)

**It does _not_ provide:**

- Command line switches for odoo server (✨ 🍰 ✨) -- if you have an appealing
  use case, submit a subcommand instead.
- Resource scheduling options (✨ 🍰 ✨) -- turn to your deployment framework
  of choice.
- Monolithic things (✨ 🍰 ✨) -- go back to jail and don't draw $10 from the
  bank.

## Spec

see manpage

<div align="center">
    <div>
        <a href="https://xoe.solutions">
            <img width="100" src="https://erp.xoe.solutions/logo.png" alt="XOE Corp. SAS">
        </a>
    </div>
    <p>
    <sub>Currently, folks <a href="https://github.com/xoe-labs/">@xoe-labs</a> try to keep up with their task to maintain this.</sub>
    </p>
    <p>
    <sub>If you're the kind of person, willing to sponsor open source projects, consider sending some spare XLM banana to <code>blaggacao*keybase.io</code></sub>
    </p>
</div>
