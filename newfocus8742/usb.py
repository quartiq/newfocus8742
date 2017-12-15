import usb.core
import usb.util

from .protocol import NewFocus8742Protocol


class NewFocus8742USB(NewFocus8742Protocol):
    eol_write = b"\r"
    eol_read = b"\r\n"

    def __init__(self, dev):
        self.dev = dev
        # dev.set_configuration()  # breaks the second invocation
        cfg = dev.get_active_configuration()
        intf = cfg[(0, 0)]
        self.ep_out = usb.util.find_descriptor(intf,
            custom_match=lambda e:
                usb.util.endpoint_direction(e.bEndpointAddress) ==
                usb.util.ENDPOINT_OUT)
        assert self.ep_out is not None
        assert self.ep_out.wMaxPacketSize == 64
        self.ep_in = usb.util.find_descriptor(intf,
            custom_match=lambda e:
                usb.util.endpoint_direction(e.bEndpointAddress) ==
                usb.util.ENDPOINT_IN)
        assert self.ep_in is not None
        assert self.ep_in.wMaxPacketSize == 64
        self.flush()

    @classmethod
    async def connect(cls, idVendor=0x104d, idProduct=0x4000, **kwargs):
        """Connect to a Newfocus/Newport 8742 controller over USB.

        Args:
            **kwargs: passed to `usb.core.find`

        Returns:
            NewFocus8742: Driver instance.
        """
        dev = usb.core.find(idProduct=idProduct, idVendor=idVendor,
                **kwargs)
        if dev is None:
            raise ValueError("Device not found")
        return cls(dev)

    def flush(self):
        """Drain the input buffer from read data."""
        while True:
            try:
                self.ep_in.read(64, timeout=10)
            except usb.core.USBError:
                break

    def close(self):
        usb.util.dispose_resources(self.dev)

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()

    def _writeline(self, cmd):
        self.ep_out.write(cmd.encode() + self.eol_write)

    async def _readline(self):
        # This is obviously not asynchronous
        r = self.ep_in.read(64).tobytes()
        assert r.endswith(self.eol_read)
        r = r[:-2].decode()
        return r
