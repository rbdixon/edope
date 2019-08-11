# eSports Leet Automatic Network Cheating Enhancement (ELANCE)

Winners never cheat. Cheaters never win. Hackers sometimes cheat.

This software implements modifications to the ANT+ messages between an ANT+ USB dongle and a computer running a virtual cycling program, such as Zwift. ELANCE requires, and will install, [USBQ](https://usbq.org). USBQ is a Python-based programming framework for monitoring and modifying USB communications.

Before proceeding with ELANCE you should verify that you can use Zwift with USBQ in pass-through mode. Run `usbq mitm` and verify that Zwift works as you would expect.

The hacks that ELANCE implements have been tested with Zwift but are not specific to Zwift in particular. The hacks may work with other virtual cycling applications.

See a talk and demo of USBQ from the DEF CON 27 presentation *[Cheating in eSports: How to Cheat at Virtual Cycling Using USB Hacks](http://edope.bike/posts/def-con-27-presentation-material-and-links/)*.

## License

This is free software distributed under the MIT license
