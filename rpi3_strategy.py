import enum

import attr
import pathlib

from labgrid.factory import target_factory
from labgrid.strategy.common import Strategy, StrategyError


class Status(enum.Enum):
    unknown, off, bootstrapped, uboot, shell = range(5)


@target_factory.reg_driver
@attr.s(eq=False)
class Rpi3Strategy(Strategy):
    """Rpi3Strategy - Strategy to switch to uboot or shell"""
    bindings = {
        "power": "PowerProtocol",
        "sdmux": "USBSDWireDriver",
        "storage": "USBStorageDriver",
        "console": "ConsoleProtocol",
        "uboot": "UBootDriver",
        "shell": "ShellDriver",
    }

    status = attr.ib(default=Status.unknown)

    def __attrs_post_init__(self):
        super().__attrs_post_init__()
        self.bootstrapped = False

    def bootstrap(self):
        self.target.activate(self.sdmux)
        self.sdmux.set_mode("host")

        self.target.activate(self.storage)

        builder = self.target.get_driver("UBootProviderDriver",
                                         allow_missing=True)
        if builder:
            image = builder.build()
        else:
            image = self.target.env.config.get_image_path("u-boot.bin")
        self.storage.write_files([image], pathlib.PurePath("/rpi3-u-boot.bin"),
                                 1, False)
        self.target.deactivate(self.storage)

        self.sdmux.set_mode("dut")
        self.bootstrapped = True

    def transition(self, status):
        if not isinstance(status, Status):
            status = Status[status]
        if status == Status.unknown:
            raise StrategyError(f"can not transition to {status}")
        elif status == self.status:
            return # nothing to do
        elif status == Status.off:
            self.target.deactivate(self.console)
            self.target.activate(self.power)
            self.power.off()
        elif status == Status.bootstrapped:
            self.bootstrap()
        elif status == Status.uboot:
            if not self.bootstrapped:
                self.transition(Status.bootstrapped)

            self.target.activate(self.console)
            # cycle power
            self.target.activate(self.power)
            self.power.cycle()
            # interrupt uboot
            #self.target.activate(self.uboot)
        elif status == Status.shell:
            # transition to uboot
            self.transition(Status.uboot)
            self.uboot.boot("")
            self.uboot.await_boot()
            self.target.activate(self.shell)
            self.shell.run("systemctl is-system-running --wait")
        else:
            raise StrategyError(f"no transition found from {self.status} to {status}")
        self.status = status

    def force(self, status):
        if not isinstance(status, Status):
            status = Status[status]
        if status == Status.off:
            self.target.activate(self.power)
        elif status == Status.uboot:
            self.target.activate(self.uboot)
        elif status == Status.shell:
            self.target.activate(self.shell)
        else:
            raise StrategyError("can not force state {}".format(status))
        self.status = status
