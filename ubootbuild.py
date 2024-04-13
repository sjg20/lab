import enum

import attr
import pathlib

from labgrid.factory import target_factory
from labgrid.strategy.common import Strategy, StrategyError
from labgrid.util.helper import processwrapper


class Status(enum.Enum):
    unknown, build = range(2)


@target_factory.reg_driver
@attr.s(eq=False)
class UBootBuildStrategy(Strategy):
    """Rpi3Strategy - Strategy to switch to uboot or shell"""
    # bindings = {}

    status = attr.ib(default=Status.unknown)

    def __attrs_post_init__(self):
        super().__attrs_post_init__()
        self.bootstrapped = False
        self.tool = 'buildman'
        self.build_base = '/tmp/b'

    def transition(self, status):
        if not isinstance(status, Status):
            status = Status[status]
        if status == Status.unknown:
            raise StrategyError(f"can not transition to {status}")
        elif status == self.build:
            cmd = [
                self.tool,
                '-o', os.path.join(self.build_base, self.board),
                '-w',
                '--board', self.board,
            ]
            processwrapper.check_output(cmd)
        else:
            raise StrategyError(f"no transition found from {self.status} to {status}")
        self.status = status

    def force(self, status):
        if not isinstance(status, Status):
            status = Status[status]
        if status == Status.off:
            self.target.activate(self.power)
        else:
            raise StrategyError("can not force state {}".format(status))
        self.status = status
