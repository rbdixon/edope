import sys
import logging

from coloredlogs import ColoredFormatter

__all__ = ['configure_logging']

FORMAT = '%(levelname)8s [%(name)24s]: %(message)s'
LOG_FIELD_STYLES = {
    'asctime': {'color': 'green'},
    'hostname': {'color': 'magenta'},
    'levelname': {'color': 'green', 'bold': True},
    'name': {'color': 'blue'},
    'programname': {'color': 'cyan'},
}


def configure_logging(level=logging.INFO):
    # Turn on logging
    root = logging.getLogger()
    root.setLevel(level)

    # plain log to file
    debug_log = logging.FileHandler('debug.log')
    debug_log.setLevel(level)
    formatter = logging.Formatter(fmt=FORMAT)
    debug_log.setFormatter(formatter)
    root.addHandler(debug_log)

    # color logs to console
    stderr_log = logging.StreamHandler(sys.stderr)
    stderr_log.setLevel(level)
    color_formatter = ColoredFormatter(fmt=FORMAT, field_styles=LOG_FIELD_STYLES)
    stderr_log.setFormatter(color_formatter)
    root.addHandler(stderr_log)
