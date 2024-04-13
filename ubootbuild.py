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
    """UBootProviderDriver - Build U-Boot image for a board

    Attributes:
        board (str): U-Boot board name, e.g. "gurnard"
        build_base (str): Base output directory for build, e.g. "/tmp/b".
            The build will taken place in build_base/board, e.g. "/tmp/b/gurnard"
        output (str): Output file to return, e.g. "u-boot.bin"
        source_dir (str): Directory containing U-Boot source (default is current
            directory)
    """
    board = attr.ib(validator=attr.validators.instance_of(str))
    build_base = attr.ib(validator=attr.validators.instance_of(str))
    output = attr.ib(default='u-boot.bin',
                     validator=attr.validators.instance_of(str))
    source_dir = attr.ib(default=os.getcwd(),
                         validator=attr.validators.instance_of(str))

    def __attrs_post_init__(self):
        super().__attrs_post_init__()
        env = self.target.env
        if env:
            self.tool = env.config.get_tool('buildman')
            self.source_dir = env.config.get_tool('buildman')
        else:
            self.tool = 'buildman'

    @Driver.check_active
    @step(title='build')
    def build(self):
        """Builds U-Boot

        Returns:
            str: Filename of build result, e.g. "u-boot.bin"
        """
        build_path = os.path.join(self.build_base, self.board)
        cmd = [
            self.tool,
            '-o', build_path,
            '-w',
            '--board', self.board,
            '-W',
        ]
        print(f"Building U-Boot for {self.board}")
        self.logger.debug(f"cwd:{os.getcwd()} cmd:{cmd}")
        processwrapper.check_output(cmd)
        fname = os.path.join(build_path, self.output)
        return fname
