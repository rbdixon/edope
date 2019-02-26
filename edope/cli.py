# -*- coding: utf-8 -*-

'''Console script for edope.'''
import sys
import click
import logging

import usbq.opts

from .log import configure_logging
from .sniff import do_sniff
from .monitor import do_monitor

log = logging.getLogger(__name__)


@click.group(invoke_without_command=True)
@click.option('--debug', is_flag=True, default=False, help='Enable debugging.')
@click.pass_context
def main(ctx, debug):
    'eSports Leet Automatic Networked Cheating Enhancement (LANCE)'

    if debug:
        configure_logging(level=logging.DEBUG)
    else:
        configure_logging(level=logging.INFO)
    return 0


@main.command()
@usbq.opts.add_options(usbq.opts.network_options)
@usbq.opts.add_options(usbq.opts.pcap_options)
@click.pass_context
def sniff(ctx, *args, **kwargs):
    'Sniff ANT+ to Zwift communications.'
    log.info('Starting ANT+ sniffer')
    do_sniff(ctx.params)


@main.command()
@usbq.opts.add_options(usbq.opts.network_options)
@usbq.opts.add_options(usbq.opts.pcap_options)
@click.pass_context
def monitor(ctx, *args, **kwargs):
    'Monitor fitness telemetry sent Zwift communications.'
    log.info('Starting monitor')
    do_monitor(ctx.params)


if __name__ == '__main__':
    sys.exit(main(auto_envvar_prefix='EDOPE'))  # pragma: no cover
