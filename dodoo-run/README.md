# `dodoo run` Component

## Abstract

`dodoo run` runs a suck-less Odoo server for servers and workers.

It implements the server components: http, bus (longpolling) & graphql.
It also implements the workers: con & queue [^1].

It does not implement a crappy scheduler. Rather (auto-)scaling and resource
management is designed to be off-handed to eg. the kubernetes scheduler.

All servers implement prometheus request / response metrics endpoints.

## Todos

- extract wkhtmltopdf as odoo dependency and patch id.actions.report to use
  (scalable) athenapdf microservice


## Spec

see man page


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
