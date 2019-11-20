# `dodoo copy` Component

## Abstract

`dodoo copy` subcommand copies a database on the given db conection and -
optionally - installs a module list and/or executes raw SQL.

Installing modules allows you to overload certain modules which prepare a
database for staging or testing environments.

Executing raw sql goes further and let's you do aribtrary stuff on your
copied database (eg. anonymize contact data or change the company name)

## Spec

```
dodoo copy [options] <source> <destination> <rawsql>
    --force-disconnect   Attempt to disconnect users from the source database.
    --install-modules    Comma separated list of addons to install.

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
