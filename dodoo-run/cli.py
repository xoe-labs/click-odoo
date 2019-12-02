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
    run as _run,
)


@click.group()
@click.option("-s", "--stateless", is_flag=True)
def run(*args, **kwargs):
    _run(*args, **kwargs)


@run.command()
@click.option("-h", "--host", default="0.0.0.0", type=str)
@click.option("-p", "--port", default=8000, type=int)
def http(*args, **kwargs):
    _http(*args, **kwargs)


@run.command()
@click.option("-h", "--host", default="0.0.0.0", type=str)
@click.option("-p", "--port", default=8000, type=int)
def bus(*args, **kwargs):
    _bus(*args, **kwargs)


@run.command()
@click.option("-h", "--host", default="0.0.0.0", type=str)
@click.option("-p", "--port", default=8075, type=int)
@click.argument("schema", type=str)
def graphql(*args, **kwargs):
    _graphql(*args, **kwargs)


@run.command()
def cron(*args, **kwargs):
    _cron(*args, **kwargs)


if __name__ == "__main__":  # pragma: no cover
    run()
