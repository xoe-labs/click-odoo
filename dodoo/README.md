# `dodoo` Base Component

## Abstract

`dodoo` is a CLI or library entrypoint to the dodoo server middleware for Odoo.

**It provides:**

- A handle to the Odoo namespace `dodoo.odoo`
- A handle to the Odoo wsgi app `dodoo.app`
- A context manager to an initialized registry `dodoo.registry(db, **kwargs)`
    - A custom context manager, cleaning up database connections
- A handle to a database connection on the default schema `dodoo.oconn(db)` ("odoo connection")
- A handle to a database connection on the dodoo schema `dodoo.dconn(db)` ("dodoo connection")
- doDoo specific namespaces:
    - `dodoo.config` - a slim doDoo api to the Odoo config
    - `dodoo.modules` - simplified doDoo api to interact with Odoo modules
         - `dodoo.modules.expand` - include all dependencies + autoinstall modules
         - `dodoo.modules.path` - get the file system path of a addon
         - `dodoo.modules.reflect(db)` - reflect module state in database
    - `dodoo.git` - doDoo api to interact with (remote) git version control
    - `dodoo.metrics` - doDoo metrics api

**It does _not_ provide:**

- Command line switches for odoo server (✨ 🍰 ✨) -- if you have an appealing use case, submit a subcommand instead.
- Resource scheduling options (✨ 🍰 ✨) -- turn to your deployment framework of choice.
- Monolithic things (✨ 🍰 ✨) -- go back to jail and don't draw $10 from the bank.

## Spec

```
dodoo <subcommand>
    --framework  Path to Odoo framework, if odoo is not in python path.
    --config     Yaml or Json config. Can be specified multiple times, merged in
                 order as specified. A sane default config for dev is shipped.
```


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
