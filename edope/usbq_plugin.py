from usbq.hookspec import hookimpl
from usbq.hookspec import USBQPluginDef


@hookimpl
def usbq_declare_plugins():
    return {
        'antdump': USBQPluginDef(
            name='antdump',
            desc='Dump ANT packets to console.',
            mod='edope.sniff',
            clsname='AntSniff',
        ),
        'monitor': USBQPluginDef(
            name='monitor',
            desc='Monitor fitness telemetry',
            mod='edope.monitor',
            clsname='FitnessMonitor',
        ),
        'epo': USBQPluginDef(
            name='epo',
            desc='Dope your way to 7 cool yellow shirts',
            mod='edope.epo',
            clsname='EPOMode',
        ),
        'slacker': USBQPluginDef(
            name='slacker',
            desc='Give your thumbs the workout they deserve!',
            mod='edope.slacker',
            clsname='SlackerMode',
        ),
    }
