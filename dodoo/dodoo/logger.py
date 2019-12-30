import logging
import sys
import threading

import click

DEFAULT_LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "()": "dodoo.logger.DefaultFormatter",
            "fmt": "%(levelprefix)s %(message)s",
        },
        "odoo": {
            "()": "dodoo.logger.DefaultFormatter",
            "fmt": "%(levelprefix)s %(message)s  -- %(dbname)s, %(name)s",
        },
        # "json": {
        #     "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
        # },
        # "filelink": {
        #     "()": "dodoo.logger.DefaultFormatter",
        #     "fmt": (
        #         "%(levelprefix)s %(dbname)s | %(message)s  (%(name)s)\n"
        #         "\tfile://%(pathname)s:%(lineno)d"
        #     ),
        # },
    },
    "handlers": {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
        },
        "odoo": {
            "formatter": "odoo",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
        },
        # "filelink": {
        #     "formatter": "filelink",
        #     "class": "logging.StreamHandler",
        #     "stream": "ext://sys.stderr",
        # },
    },
    "loggers": {
        "": {"handlers": ["default"], "level": "INFO"},
        "odoo": {"handlers": ["odoo"], "level": "INFO", "propagate": False},
    },
}


class ColourizedFormatter(logging.Formatter):
    """
    A custom log formatter class that:
    * Outputs the LOG_LEVEL with an appropriate color.
    """

    level_name_colors = {
        logging.DEBUG: lambda level_name: click.style(str(level_name), fg="cyan"),
        logging.INFO: lambda level_name: click.style(str(level_name), fg="green"),
        logging.WARNING: lambda level_name: click.style(str(level_name), fg="yellow"),
        logging.ERROR: lambda level_name: click.style(str(level_name), fg="red"),
        logging.CRITICAL: lambda level_name: click.style(
            str(level_name), fg="bright_red"
        ),
    }

    def __init__(self, fmt=None, datefmt=None, style="%"):
        self.use_colors = self.should_use_colors()
        super().__init__(fmt=fmt, datefmt=datefmt, style=style)

    def color_level_name(self, level_name, level_no):
        default = lambda level_name: str(level_name)  # noqa: E731
        func = self.level_name_colors.get(level_no, default)
        return func(level_name)

    def should_use_colors(self):
        return True

    def formatMessage(self, record):
        levelname = record.levelname
        seperator = " " * (8 - len(record.levelname))
        dbname = getattr(threading.current_thread(), "dbname", "***") or "***"
        name = record.name
        if self.use_colors:
            levelname = self.color_level_name(levelname, record.levelno)
            dbname = click.style(dbname, fg="blue")
            name = click.style(name, bold=True)

        record.__dict__["levelprefix"] = levelname + ":" + seperator
        record.__dict__["dbname"] = dbname
        record.__dict__["name"] = name
        return super().formatMessage(record)


class DefaultFormatter(ColourizedFormatter):
    def should_use_colors(self):
        return sys.stderr.isatty()
