#!/usr/bin/env python3

import argparse
import os
import asyncio

from sipyco.pc_rpc import simple_server_loop
from sipyco import common_args


def get_argparser():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tcp", help="use TCP device, else use first "
                                      "USB device")
    parser.add_argument("--simulation", action="store_true",
                        help="simulation device")

    common_args.simple_network_args(parser, 3257)
    common_args.verbosity_args(parser)
    return parser


def main():
    args = get_argparser().parse_args()
    common_args.init_logger_from_args(args)

    if os.name == "nt":
        asyncio.set_event_loop(asyncio.ProactorEventLoop())
    loop = asyncio.get_event_loop()

    if args.simulation:
        from .sim import NewFocus8742Sim
        dev = loop.run_until_complete(NewFocus8742Sim.connect())
    elif args.tcp:
        from .tcp import NewFocus8742TCP
        dev = loop.run_until_complete(NewFocus8742TCP.connect(args.tcp))
    else:
        from .usb import NewFocus8742USB
        dev = loop.run_until_complete(NewFocus8742USB.connect())

    try:
        simple_server_loop({"newfocus8742": dev},
                           common_args.bind_address_from_args(args), args.port)
    except KeyboardInterrupt:
        pass
    finally:
        dev.close()


if __name__ == "__main__":
    main()
