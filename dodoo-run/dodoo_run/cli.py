#!/usr/bin/env python3
# =============================================================================
# Created By : David Arnold
# Part of    : xoe-labs/dodoo
# =============================================================================
"""This module implements the dodoo run cli subcommand."""


import click

from . import (
    bus as _bus,
    cron as _cron,
    graphql as _graphql,
    http as _http,
    queue as _queue,
)


@click.group()
def run():
    pass


@run.command()
@click.argument("addr", default="0.0.0.0", type=str)
@click.argument("port", default=8069, type=int)
def http(*args, **kwargs):
    _http(*args, **kwargs)


@run.command()
@click.argument("host", default="0.0.0.0", type=str)
@click.argument("addr", default=8072, type=int)
def bus(*args, **kwargs):
    _bus(*args, **kwargs)


@run.command()
@click.argument("schema", type=str)
@click.argument("addr", default="0.0.0.0", type=str)
@click.argument("port", default=8075, type=int)
def graphql(*args, **kwargs):
    _graphql(*args, **kwargs)


@run.command()
def cron(*args, **kwargs):
    _cron(*args, **kwargs)


@run.command()
def queue(*args, **kwargs):
    _queue(*args, **kwargs)


if __name__ == "__main__":  # pragma: no cover
    run()
