import attr
import os

from labgrid.driver.common import Driver
from labgrid.factory import target_factory
from labgrid.step import step
from labgrid.driver.exception import ExecutionError
from labgrid.util.helper import processwrapper

@target_factory.reg_driver
@attr.s(eq=False)
class UBootProviderDriver(Driver):
    """UBootProviderDriver - Build U-Boot image for a board"""
    board = attr.ib(validator=attr.validators.instance_of(str))
    build_base = attr.ib(validator=attr.validators.instance_of(str))
    output = attr.ib(default='u-boot.bin',
                     validator=attr.validators.instance_of(str))

    def __attrs_post_init__(self):
        super().__attrs_post_init__()
        if self.target.env:
            self.tool = self.target.env.config.get_tool('buildman')
        else:
            self.tool = 'buildman'

    @Driver.check_active
    @step(title='build')
    def build(self):
        build_path = os.path.join(self.build_base, self.board)
        cmd = [
            self.tool,
            '-o', build_path,
            '-w',
            '--board', self.board,
            '-W',
        ]
        print(f"Building U-Boot for {self.board}")
        self.logger.debug("cwd:{os.getcwd()} cmd:{cmd}")
        processwrapper.check_output(cmd)
        fname = os.path.join(build_path, self.output)
        return fname
