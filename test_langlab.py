"""pyloco netcdf module
"""

from __future__ import unicode_literals

import os
import pyloco
import tempfile
import shutil
import langlab

here, myname = os.path.split(__file__)

greeting = "Hello, World!"

helloworld_c = """/* helloworld.c test program */
#include <stdio.h>
int main()
{
   printf("%s");
   return 0;
}
""" % greeting

srcname = "helloworld"
srcfile = srcname + ".c"
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
        self.outpath = os.path.join(self.tempdir, outfile)

        with open(self.srcpath, "w") as fsrc:
            fsrc.write(helloworld_c)

    def tearDown(self):

        shutil.rmtree(self.tempdir)

    def test_shell_compile(self):

        with langlab.workdir(self.tempdir) as cwd:

            argv = [
                "gcc -o %s %s" % (self.outpath, self.srcpath),
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
            self.assertEqual(fwd["stdout"], greeting)
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


test_classes = (TaskLangLabTests,)
