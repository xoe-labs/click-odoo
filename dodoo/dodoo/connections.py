# =============================================================================
# Created By : David Arnold
# Part of    : xoe-labs/dodoo
# =============================================================================
"""This module implements the dodoo database connection api and helpers"""

import logging

import psycopg2

_log = logging.getLogger(__name__)


class SchemaNotCreatedError(Exception):
    pass


class SchemaCursor:
    def __init__(self, dsn, dry=False, schema=None):
        self.dsn = dsn
        self.dry = dry
        self.schema = schema

    def __enter__(self):
        self.conn = psycopg2.connect(self.dsn)
        self.cr = self.conn.cursor()
        self.cr.execute(f"SET search_path TO {self.schema}")

        return self.cr

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.dry:
            self.conn.rollback()
        elif isinstance(exc_type, psycopg2.Error):
            self.conn.rollback()
            self.conn.close()
            raise exc_type(exc_val)
        else:
            self.conn.commit()
        self.conn.close()


class DodooCursor(SchemaCursor):
    def __init__(self, dsn, dry=False):
        super().__init__(dsn, dry, "dodoo")


class PublicCursor(SchemaCursor):
    def __init__(self, dsn, dry=False):
        super().__init__(dsn, dry, "public")


class OdooCursor(SchemaCursor):
    def __init__(self, dsn, dry=False):
        super().__init__(dsn, dry, "odoo")


def create_custom_schema_layout(dsn, schemata):
    qry = ""
    for schema in schemata:
        qry += f"CREATE SCHEMA IF NOT EXISTS {schema};"
    with PublicCursor(dsn) as cr:
        try:
            cr.execute(qry)
        # https://www.postgresql.org/docs/current/errcodes-appendix.html#ERRCODES-TABLE
        except psycopg2.Error as e:
            _log.critical(
                "Could not create dodoo's custom database schema.\n"
                f"\tdsn='{cr.connection.dsn}' - error='{e.pgerror}'.\n"
                "\tPlease fix in your database."
            )
            raise SchemaNotCreatedError(e)
        except Exception as e:
            _log.critical(
                "Could not create dodoo's custom database schema.\n"
                f"\tdsn='{cr.connection.dsn}'\n"
                "\tPlease resolve the error."
            )
            raise SchemaNotCreatedError(e)


def create_readonly_user_for_schema(dsn, schema):
    with PublicCursor(dsn) as cr:
        ro_user = f"{dsn.connections.info.user}-readonly"
        qry = (
            f"CREATE ROLE IF NOT EXISTS {ro_user};"
            f"GRANT CONNECT ON DATABASE {cr.dbname} TO {ro_user};"
            f"GRANT SELECT ON ALL TABLES IN SCHEMA {schema} TO {ro_user};"
            f"ALTER DEFAULT PRIVILEGES IN SCHEMA {schema}"
            f"  GRANT SELECT ON TABLES TO {ro_user};"
        )
        try:
            cr.execute(qry)
        # https://www.postgresql.org/docs/current/errcodes-appendix.html#ERRCODES-TABLE
        except Exception as e:
            _log.warning(
                f"Could not create readonly user '{ro_user}' "
                f"on schema '{schema} in databas {cr.dbname}."
            )
            raise e
