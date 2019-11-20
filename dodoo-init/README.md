# `dodoo init` Component

## Abstract

`dodoo init` subcommand initializes a database on the given db conection and -
optionally - installs a module list and/or executes raw SQL.

It keeps a specially prefixed  db / filstore cache so that subsequent inits are
accelerated. A hash is built over the listed module dirs to keep cache
consistent with your code and clear as needed.

Executing raw SQL permits you to do advanced, eventually templated, database
seeding setting for example main company data or certain config settings.


## Spec

```
dodoo init [options] <newdatabase> <rawsql>
    --install-modules    Comma separated list of addons to install.
    --with-demo          Load Odoo demo data.
    --no-cache           Don't use cache.
    --cache-prefix       Cache prefix. Caution: identifies clearble artefacts.
    --cache-max-age      Clear cache after so many days of non-usage.
                         Default: 30. Use -1 to disable.
    --cache-max-size     Keep N most recently used cache templates.
                         Default: 5. Use -1 to disable. Use 0 to empty.

    --help      This help

    All options can be supplied with environment variables:
        Uppercase / strip inital '--' / replace '-' by '_' / prefix `DODOO_`.
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
