# `dodoo backup` Component

## Abstract

`dodoo backup` subcommand snpashots a database and it's filestore into a local
filemount and ships a **strongly** encrypted _deduplicating_ backup
bandwith-efficiently (`zlib`) to a remote host over ssh using `borg`.

No GnuGP nighmare as in `duplicity`. True BLAKE2b. Period.

It can retrieve backups form the remote and restore them into an existing or
fresh database.

You need to deploy `borg` on the backup server. Backups give you peace of mind,
so _know_ what you do. That's not asking too much. [RTFM](https://borgbackup.readthedocs.io/en/stable/deployment.html)


## Spec

<sub>Encryption/Auth key provided by the `dodoo` server instance</sub>

```
dodoo backup [options] <subcommand>


Subcommands:
    init [options] <remote>
    	--storage-quota 5G   Set storage quota of the new repository.
    prune
        --keep-daily    7
	    --keep-weekly   4
	    --keep-monthly  6
	create <databasename> <tag>
	restore <tag> <databasename>

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
