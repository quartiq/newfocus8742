import time
import logging
import asyncio

from newfocus8742.usb import NewFocus8742USB as USB
from newfocus8742.tcp import NewFocus8742TCP as TCP


def main():
    logging.basicConfig(level=logging.DEBUG)
    loop = asyncio.get_event_loop()
    loop.set_debug(False)
    async def run():
        with USB.connect() as dev:
        # with await TCP.connect("8742-37565") as dev:
            # await test(dev)
            # await dump(dev)
            dev.stop()
            dev.abort()
            print(await dev.error_message())
            print(await dev.get_velocity(1))
            dev.set_velocity(1, 2000)
            print(await dev.get_velocity(1))
            print(await dev.error_code())
            print(await dev.identify())
            print(await dev.get_home(1))
            print(await dev.get_position(1))
            print(await dev.get_relative(1))
            dev.set_relative(1, 10)
            await dev.finish(1)
    loop.run_until_complete(run())


async def dump(dev):
    for i in range(4):
        for cmd in "AC DH MD MV PA PR QM TP VA".split():
            print(1 + i, cmd, await dev.ask(cmd + "?", 1 + i))
    for cmd in ("SA SC SD TB TE VE ZZ "
                "GATEWAY HOSTNAME IPADDR IPMODE MACADDR NETMASK "
                ).split():
        print(cmd, await dev.ask(cmd + "?"))



async def test(dev):
    print(dev)
    m = 2
    dev.do("VA", m, 2000)
    dev.do("AC", m, 100000)
    for i in range(100):
        dev.do("PR", m, 100)
        while not int(await dev.ask("MD?", m)):
            await asyncio.sleep(.001)
        print(".")
        await asyncio.sleep(.1)
    print(await dev.ask("TP?", m))
    print(await dev.ask("QM?", m))


if __name__ == "__main__":
    main()
