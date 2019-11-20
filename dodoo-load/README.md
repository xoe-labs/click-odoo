# `dodoo load` Component

## Abstract

`dodoo load` subcommand provides state and boilerplate for the loading part of
ETL projects.

It can take a file or stream and load data into the given database, it persists
loading state with appropriate (augmented) metadata into the `dodoo` schema and
resumes accordingly.

It toposorts input to according to model dependencies and always loads in the
right order. It also cares to loading order for hierarchies through locks.

After a loading is done, the loading state can be cleaned or reported on.


## Spec
```
dodoo load [options] <database> <stream or file>
    --with-history       Activate chatter history generation. (Default: off)
    --batch-size         Batch size; recent Odoo batch create efficiently.
    --emulate-onchange   Emulate onchange actions if loaded fields trigger.

Subcommands:
    report <database>   Report on loaded data.
    prune <database>    Clean state about the entire ETL project.
    	--model             Just prune specific models.

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
