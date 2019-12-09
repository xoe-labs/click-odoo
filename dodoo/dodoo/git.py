#!/usr/bin/env python3
# =============================================================================
# Created By : David Arnold
# Part of    : xoe-labs/dodoo
# =============================================================================
"""This module implements the dodoo.git api"""

__all__ = ["Repo", "fetch_remote", "get_changed_odoo_modules_compared_to"]

import logging
import os

import pygit2

from dodoo.interfaces import odoo

_log = logging.getLogger(__name__)

current_working_directory = os.getcwd()
repository_path = pygit2.discover_repository(os.getcwd())
Repo = pygit2.Repository(repository_path)
cwd_description = Repo.describe(dirty_suffix="-dirty")
_log.info(f"Git workdir state {cwd_description}")

# ==============
# Useful Errors
# ==============


class RemoteNotExistsError(Exception):
    pass


class CommitIshNotExistsError(Exception):
    pass


# ================
# Utility Wrappers
# ================


def fetch_remote(remote):
    try:
        Repo.remotes[remote].fetch()
    except KeyError:
        raise RemoteNotExistsError(f"Remote {remote} is not configured.")


def get_changed_odoo_modules_compared_to(commit_ish):
    try:
        diff = Repo.diff(commit_ish)
    except KeyError:
        raise CommitIshNotExistsError(f"Commit-ish {commit_ish} not found.")
    change_modules = []
    for patch in diff:
        new_path = patch.delta.new_file.path
        module = odoo.Modules().deduce_module_name_from(new_path)
        if not module:
            continue
        change_modules.append()
