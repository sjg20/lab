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
        build_base (str):
        output (str): Output file to return, e.g. "u-boot.bin"
        source_dir (str): Directory containing U-Boot source (default is current
            directory)

    Paths (environment configuration):
        uboot_build_base: Base output directory for build, e.g. "/tmp/b".
            The build will taken place in build_base/board, e.g. "/tmp/b/gurnard"
    """
    board = attr.ib(validator=attr.validators.instance_of(str))
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
        self.build_base = env.config.get_path("uboot_build_base")
        self.workdirs = env.config.get_path("uboot_workdirs")

    @Driver.check_active
    @step(title='build')
    def build(self):
        """Builds U-Boot

        Performs an incremental build of U-Boot for the selected board,
        returning a single output file produced by the build

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

    def setup_worktree(self):
        """Make sure there is a worktree for the current board

        If the worktree directory does not exist, it is created
        """
        workdir = os.path.join(self.workdirs, self.board)
        if not os.path.exists(workdir):
            cmd = [
                'git',
                '--git-dir', self.source_dir,
                'worktree',
                'add',
                self.board,
                '--detach',
            ]
            self.logger.info(f"Setting up worktree in {workdir}")
            processwrapper.check_output(cmd, cwd=self.workdirs)

    def select_commit(self, commit):
        """Select a particular commit in the worktree

        Args:
            commit (str): Commit to select (hash or branch name)
        """
        workdir = os.path.join(self.workdirs, self.board)
        cmd = [
            'git',
            '--git-dir', workdir,
            'checkout',
            commit,
        ]
        self.logger.info(f"Checking out {commit}")
        processwrapper.check_output(cmd, cwd=self.workdirs)
