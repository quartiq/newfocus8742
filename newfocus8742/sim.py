import asyncio
import logging
import re
import random


from .protocol import NewFocus8742Protocol


logger = logging.getLogger(__name__)


class NewFocus8742Sim(NewFocus8742Protocol):
    channels = 4

    def __init__(self):
        self.position = [0 for i in range(self.channels)]
        self.home = [0 for i in range(self.channels)]
        self.target = [0 for i in range(self.channels)]
        self.velocity = [2000 for i in range(self.channels)]
        self.acceleration = [100000 for i in range(self.channels)]
        self.pending = []

    @classmethod
    async def connect(cls, *args, **kwargs):
        """Connect to a Newfocus/Newport 8742 controller simulation.

        Args:
            any: ignored

        Returns:
            NewFocus8742: Driver instance.
        """
        return cls()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()

    def close(self):
        if self.pending:
            raise ValueError("pending data {}".format(self.pending))

    def _writeline(self, cmd):
        m = re.match(r"^(?P<xx>\d)?\s*\*?(?P<cmd>[a-zA-Z]+)\s*"
                r"(?P<nn>\d+(,\s*\d+)*)?(?P<ask>\?)?$", cmd)
        assert m
        d = m.groupdict()
        if d["ask"] == "?":
            f = getattr(self, "ask_{}".format(d["cmd"].lower()), None)
        else:
            f = getattr(self, "do_{}".format(d["cmd"].lower()), None)
        kwargs = {}
        if d["xx"] is not None:
            kwargs["xx"] = int(d["xx"])
        if d["nn"]:
            args = tuple(int(i) for i in d["nn"].split(","))
        else:
            args = ()
        ret = None
        if f:
            ret = str(f(*args, **kwargs))
        else:
            logger.warning("cmd ignored: %s", d["cmd"])
        if d["ask"] == "?":
            assert ret
            self.pending.append(ret)

    async def _readline(self):
        return self.pending.pop(0)

    def ask_tb(self):
        return "0, NO ERROR"

    def ask_te(self):
        return 0

    def ask_idn(self):
        return "Newfocus 8742, simulated"

    def do_va(self, nn, xx):
        assert 1 <= xx <= 4
        self.velocity[xx - 1] = nn

    def ask_va(self, xx):
        assert 1 <= xx <= 4
        return self.velocity[xx - 1]

    def do_pa(self, nn, xx):
        assert 1 <= xx <= 4
        self.position[xx - 1] = nn

    def ask_pa(self, xx):
        assert 1 <= xx <= 4
        return self.position[xx - 1]

    def do_pr(self, nn, xx):
        assert 1 <= xx <= 4
        self.position[xx - 1] += nn

    def ask_pr(self, xx):
        assert 1 <= xx <= 4
        return 0

    def ask_tp(self, xx):
        assert 1 <= xx <= 4
        return self.position[xx - 1] - self.home[xx - 1]

    def do_ac(self, nn, xx):
        assert 1 <= xx <= 4
        self.acceleration[xx - 1] = nn

    def ask_ac(self, xx):
        assert 1 <= xx <= 4
        return self.acceleration[xx - 1]

    def do_sm(self, xx=None):
        pass

    def do_ab(self, xx=None):
        pass

    def do_qm(self, *nn, xx):
        assert 1 <= xx <= 4
        pass

    def ask_qm(self, xx):
        return 2

    def ask_dh(self, xx):
        assert 1 <= xx <= 4
        return self.home[xx - 1]

    def do_dh(self, *nn, xx):
        assert 1 <= xx <= 4
        nn = nn[0] if nn else 0
        self.position[xx - 1] += self.home[xx - 1] - nn
        self.home[xx - 1] = nn

    def ask_md(self, xx):
        assert 1 <= xx <= 4
        return random.randint(0, 1)

    def do_mv(self, *nn, xx):
        assert 1 <= xx <= 4
        nn = nn[0] if nn else 1
        self.position[xx - 1] += nn

    def ask_sa(self):
        return 0

    def ask_sc(self):
        return 0

    def ask_sd(self):
        return 0

    def ask_ve(self):
        return self.ask_idn()

    def ask_zz(self):
        return 0

    def ask_gateway(self):
        return 0

    def ask_netmask(self):
        return 0

    def ask_hostname(self):
        return 0

    def ask_ipaddr(self):
        return 0

    def ask_ipmode(self):
        return 0

    def ask_macaddr(self):
        return 0
