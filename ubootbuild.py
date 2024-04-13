import attr

from labgrid.driver.common import Driver
from labgrid.factory import target_factory
from labgrid.step import step
from labgrid.driver.exception import ExecutionError
from labgrid.util.helper import processwrapper

@target_factory.reg_driver
@attr.s(eq=False)
class UBootBuildDriver(Driver):
    """UBootBuildDriver - Build U-Boot image for a board"""
    bindings = {
        #"mux": {"USBSDWireDevice", "NetworkUSBSDWireDevice"},
    }

    def __attrs_post_init__(self):
        super().__attrs_post_init__()
        if self.target.env:
            self.tool = self.target.env.config.get_tool('buildman')
        else:
            self.tool = 'buildman'
        self.build_base = '/tmp/b'
        self.board = 'rpi_3_32b'

    @Driver.check_active
    @step(title='build')
    def build(self):
        cmd = [
            self.tool,
            '-o', os.path.join(self.build_base, self.board),
            '-w',
            '--board', self.board,
        ]
        processwrapper.check_output(cmd)
