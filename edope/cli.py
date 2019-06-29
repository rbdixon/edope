# -*- coding: utf-8 -*-
'''Console script for edope.'''
import logging
import sys

import click
import click_config_file
import usbq.opts
from usbq.pm import AVAILABLE_PLUGINS

from . import __version__
from .epo import do_epo
from .log import configure_logging
from .monitor import do_monitor
from .slacker import do_slacker
from .sniff import do_sniff

log = logging.getLogger(__name__)


@click.group(invoke_without_command=True)
@click.option('--debug', is_flag=True, default=False, help='Enable debugging.')
@click.pass_context
@click_config_file.configuration_option(cmd_name='edope', config_file_name='edope.cfg')
def main(ctx, debug):
    'eSports Leet Automatic Networked Cheating Enhancement (LANCE)'

    if ctx.invoked_subcommand is None:
        click.echo(f'edope version {__version__}\n')
        click.echo(ctx.get_help())
        click.echo('\nAvailable plugins:\n')
        for pd in sorted(AVAILABLE_PLUGINS.values(), key=lambda pd: pd.name):
            click.echo(f'- {pd.name}: {pd.desc}')

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


@main.command()
@usbq.opts.add_options(usbq.opts.network_options)
@usbq.opts.add_options(usbq.opts.pcap_options)
@click.option(
    '--power-boost', default=2, type=float, help='Multiply your power by a factor.'
)
@click.option(
    '--peak-power-limit',
    default=6.95,
    type=float,
    help='Do not exceed this watt/kg level or they will know you are cheating.',
)
@click.option(
    '--weight',
    default=84,
    type=float,
    help='Your in-game mass (kg) used for watt/kg calculations.',
)
@click.option(
    '--flat/--no-flat',
    is_flag=True,
    default=True,
    help='Make the world flat just for you.',
)
@click.pass_context
def epo(ctx, *args, **kwargs):
    'Sustain performance with less effort and more guilt.'
    log.info('Starting EPO mode')
    do_epo(ctx.params)


@main.command()
@usbq.opts.add_options(usbq.opts.network_options)
@usbq.opts.add_options(usbq.opts.pcap_options)
@click.option(
    '--peak-power-limit',
    default=6.95,
    type=float,
    help='Do not exceed this watt/kg level or they will know you are cheating.',
)
@click.option(
    '--weight',
    default=84,
    type=float,
    help='Your in-game mass (kg) used for watt/kg calculations.',
)
@click.pass_context
def slacker(ctx, *args, **kwargs):
    'Why sweat even a little?'
    log.info('Starting slacker mode')
    do_slacker(ctx.params)


if __name__ == '__main__':
    sys.exit(main())  # pragma: no cover
