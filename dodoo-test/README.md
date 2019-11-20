# `dodoo test` Component

## Abstract

`dodoo test` subcommand initializes a database on the given db conection and -
optionally - executes the tests in the given test mode.

It does not recreate databases, therefore non-idempotent tests have to be dealt
with. Those, however are rare in recent odoo versions. If you hit one, you might
use patches `odooup patch` to remedy.

It can be executed in two flavors: default and pytest.

Default mode comes with auto-detection modes and let's you filter on Odoo's test
tags. For weekly test, you can forc include certain modules, you also can
exclude notoriously unrelated failing test from autodetected module sets.

While pytest already ships with a built in humran friendly report format,
default mode emulates a custom, but human & CI-friendly test report.


## Spec
```
dodoo test <subcommand>

Subcommands:
    default [options] <database>
		--detect-mode [git]  Strategy to autodetect eligible tests.
							 Default: git
			--git-dir        Git bare repository (".git") dir to compare with.
	    --exclude-modules    Exclude (auto-detected) modules from tests.
	    --include-modules    Force to include modules for tests.
	    --filter-tags        Filter on test tags.

    pytest <database> <pytestargs>

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
