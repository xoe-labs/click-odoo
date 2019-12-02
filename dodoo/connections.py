# =============================================================================
# Created By : David Arnold
# Part of    : xoe-labs/dodoo
# =============================================================================
"""This module implements the dodoo.oconn and dodoo.dconn connection api"""

import psycopg2


class SchemaNotCreatedError(Exception):
    pass


class SchemaCursor:
    def __init__(self, dsn, dry=False, schema=None):
        self.dsn = dsn
        self.dry = dry
        self.schema = schema

    def __enter__(self):
        self.conn = psycopg2.connect(self.dsn)
        self.cur = self.conn.cursor()
        self.cur.execute(f"SET search_path TO {self.schema}")

        return self.cur

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.dry:
            self.conn.rollback()
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
            raise SchemaNotCreatedError(
                "Could not create dodoo's custom database schema.\n"
                f"\tdsn='{cr.connection.dsn}' - error='{e.pgerror}'.\n"
                "\tPlease fix in your database."
            )
