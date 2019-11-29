# `dodoo run` Component

## Abstract

`dodoo run` runs a suck-less Odoo server.

It implements the three[^1] Odoo tiers as subcommands. Every tier is run as a single process where resource management is off-loeaded to an external
scheduler (just like Odoo.sh).

[^1]: `OCA/queue` and a separate pdf renderer such as `athenapdf` (drop in for
`wkhtmltopdf`) might be supported at some point.


subcommand initializes a database on the given db conection and -
optionally - installs a module list and/or executes raw SQL.

It keeps a specially prefixed  db / attachment cache so that subsequent inits
are accelerated. A hash is built over the listed module dirs to keep cache
consistent with your code and clear as needed.

Executing raw SQL permits you to do advanced, eventually templated, database
seeding setting for example main company data or certain config settings.


## Spec

```

dodoo run [option] <subcommand>
    --stateless  use redis for session store, allow multiple server keys
                 to run server database, advise running server keys through
                 db and on stateful folders: if not consistent, fail critically.
    --stateful   advise server key to dodoo db scheme and block launching
                 with a different server key. Default.

Subcommands:
    http <socket> run the primary http server
    bus <socket>  run the longpolling server (in multi-threaded mode)
    cron         run the cron job once (scheduled externally)
    // queue     run the queue job once (scheduled externally)
    // renderer  run the pdf renderer with separate resource constraints

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
