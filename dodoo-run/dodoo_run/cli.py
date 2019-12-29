#!/usr/bin/env python3
# =============================================================================
# Created By : David Arnold
# Part of    : xoe-labs/dodoo
# =============================================================================
"""This module implements the dodoo run cli subcommand."""

import ipaddress

import click
import click_pathlib

from . import (
    bus as _bus,
    cron as _cron,
    graphql as _graphql,
    http as _http,
    queue as _queue,
)


def validate_ip(ctx, param, value):
    try:
        ipaddress.ip_address(value)
    except ValueError:
        raise click.BadParameter(f"{value} is not a valid IP address.")


def validate_port(ctx, param, value):
    if not 0 <= value <= 65535:
        raise click.BadParameter(f"{value} is not a valid port value.")


@click.group()
def run():
    # TODO: Ideas ...
    # ... Patcher feature-flag to use athenapdf microservice instead of wkhtmltopdf
    #
    pass


@run.command()
@click.argument("addr", default="0.0.0.0", type=str, callback=validate_ip)
@click.argument("port", default=8069, type=int, callback=validate_port)
def http(*args, **kwargs):
    _http(*args, **kwargs)


@run.command()
@click.argument("host", default="0.0.0.0", type=str, callback=validate_ip)
@click.argument("addr", default=8072, type=int, callback=validate_port)
def bus(*args, **kwargs):
    _bus(*args, **kwargs)


@run.command()
@click.argument(
    "schema", type=click_pathlib.Path(dir_okay=False, exists=True, resolve_path=True)
)
@click.argument("addr", default="0.0.0.0", type=str, callback=validate_ip)
@click.argument("port", default=8075, type=int, callback=validate_port)
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
