"""pyloco netcdf module
"""

from __future__ import unicode_literals

import os
import pyloco
import tempfile
import shutil
import langlab

here, myname = os.path.split(__file__)

res_in = """
static const char number_message[] = "Input number is %d!";
"""

number_c = """/* number.c test program */
#include <stdio.h>
#include <res.in>

int main()
{
   printf(number_message, NUMBER);
   return 0;
}
"""

srcname = "number"
srcfile = srcname + ".c"

resname = "res"
resfile = resname + ".in"

outfile = srcname + ".exe"

class TaskLangLabTests(pyloco.TestCase):

    def __init__(self, *vargs, **kwargs):

        super(TaskLangLabTests, self).__init__(*vargs, **kwargs)

        self.gcc = langlab.which("gcc")

        self.argv = [
            "--debug",
        ]

    def setUp(self):

        assert self.gcc is not None
        self.tempdir = tempfile.mkdtemp()

        self.srcpath = os.path.join(self.tempdir, srcfile)

        with open(self.srcpath, "w") as fsrc:
            fsrc.write(number_c)

        self.resdir = os.path.join(self.tempdir, "resource")
        self.respath = os.path.join(self.resdir, resfile)
        os.makedirs(self.resdir)

        with open(self.respath, "w") as frsc:
            frsc.write(res_in)

        self.outpath = os.path.join(self.tempdir, outfile)
        self.command = ("%s -v -o %s %s -D NUMBER=1 -I %s" %
                        ("gcc", self.outpath, self.srcpath, self.resdir))

    def tearDown(self):

        shutil.rmtree(self.tempdir)

    def test_shell_compile(self):

        with langlab.workdir(self.tempdir) as cwd:

            argv = [
                self.command,
                "--cwd", cwd.path,
            ]

            ret, fwd = langlab.perform("build", argv=argv)
            self.assertEqual(ret, 0)
            self.assertEqual(fwd["stdout"], "")
            self.assertEqual(fwd["stderr"], "")

            argv = [
                self.outpath,
                "--cwd", cwd.path,
            ]

            ret, fwd = langlab.perform("run", argv=argv)
            self.assertEqual(ret, 0)
            self.assertEqual(fwd["stdout"], "Input number is 1!")
            self.assertEqual(fwd["stderr"], "")

            argv = [
                "rm -f %s" % self.outpath,
                "--cwd", cwd.path,
            ]

            ret, fwd = langlab.perform("clean", argv=argv)
            self.assertEqual(ret, 0)
            self.assertEqual(fwd["stdout"], "")
            self.assertEqual(fwd["stderr"], "")

            self.assertTrue(not os.path.isfile(self.outpath))

    def test_tree(self):

        from langlab.tree import Tree, Node

#    def test_trace(self):
#
#        tracefile = os.path.join(self.tempdir, "trace.log")
#
#        argv = [
#            self.command,
#            tracefile,
#        ]
#
#        ret, fwd = langlab.perform("trace", argv=argv)
#        self.assertEqual(ret, 0)
#        self.assertEqual(fwd["stdout"], "")
#        self.assertEqual(fwd["stderr"], "")

test_classes = (TaskLangLabTests,)
