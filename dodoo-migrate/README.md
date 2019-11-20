# `dodoo migrate` Component

## Abstract

`dodoo migrate` subcommand manages the complete database upgrade including
integration with remote uprade services such as Odoo EE.

It uses a descriptive migration path aligned with semantic project versioning
derived from a yaml file expected to be checked into source code.

A descriptive migration path preserves history and provides for rollbacks.

It also produces a backup snapshot just before migrating.

To make migrations atomic transactions in the face of the user, a light
splashscreen server with configurable templates informs the user about the
maintenance.

It coincidentially ships with openupgradelib and odoo's own leaked migration
library for delivering on advanced migration scripts.

In order to keep migration management apart from main code (ie. to replicate
Odoo's service model for own modules), this command is able to overlay a
migration folder tree before loading the server.

State is kept in a special purpose database schema. TODO: move the schema to
up to the `dodoo` command - we never know what it might be good for.


## Spec

```
dodoo migrate [options] <database>
    --spec      The yaml file containing the migration steps.
    			Default: `./migration.yaml`
    --overlay   A migration directory overlay. (optional)
    --until     Version to migrate to (included). (optional)

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
