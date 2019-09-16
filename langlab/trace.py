# -*- coding: utf-8 -*-

import sys
import os
import subprocess

from pyloco import Task, system
import langlab


# command is a list
def run_command(command):
    p = subprocess.Popen(command,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT)
    return iter(p.stdout.readline, b'')


class TracerApp(Task):
    "trace process"

    _name_ = "trace"
    _version_ = "0.1.0"

    def __init__(self, parent):


        self.add_data_argument("command", type=str, help="command to preprocess an app.")

#
#        self.register_forward("retval", type=int, help="return value")
#        self.register_forward("stdout", type=str, help="standard output")
#        self.register_forward("stderr", type=str, help="standard error")

    def perform(self, targs):

        self.strace = langlab.which("strace")
        if not os.path.isfile(self.strace):
            raise Exception("'strace' is not found.")


        # TODO: check if strace works properly


        with langlab.tempdir() as temp:
            outpath = os.path.join(temp.path, "strace.log")

                #"-o", outpath,

            argv = [
                self.strace,
                "-f", "-q", "-s", "100000", "-e", "trace=execve", "-v",
                "--", "/bin/sh", "-c", "'%s'" % targs.command
            ]
            #command = ("{0} -o {1} -f -q -s 100000 -e trace=execve -v "
            #           "-- /bin/sh -c '{2}'".format(self.strace, outpath, targs.command))

            for line in run_command(argv):
                print(line)
                print("-----------------------------------------------------------------------")

        #ret, out, err = system(command)

        #import pdb; pdb.set_trace()
        #print(ret, out, err)
        #self.add_forward(retval=ret, stdout=out, stderr=err)
