# -*- coding: utf-8 -*-

from pyloco import Task, system

class CleanApp(Task):
    "clean intermittent files generated during compiling an application"

    _name_ = "clean"
    _version_ = "0.1.0"

    def __init__(self, parent):

        self.add_data_argument("command", type=str, help="command to clean an app.")

        self.add_option_argument("--cwd", type=str, help="working directory.")

        self.register_forward("retval", type=int, help="return value")
        self.register_forward("stdout", type=str, help="standard output")
        self.register_forward("stderr", type=str, help="standard error")

    def perform(self, targs):

        ret, out, err = system(targs.command, cwd=targs.cwd)

        self.add_forward(retval=ret, stdout=out, stderr=err)
