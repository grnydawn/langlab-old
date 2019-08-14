"""pyloco netcdf module
"""

from __future__ import unicode_literals

import os
import pyloco

here, myname = os.path.split(__file__)

class TaskLangLabTests(pyloco.TestCase):

    def __init__(self, *vargs, **kwargs):

        super(TaskLangLabTests, self).__init__(*vargs, **kwargs)

        self.argv = [
            "--debug",
        ]

    def setUp(self):
        pass
        #if os.path.exists(imgfile):
        #    os.remove(imgfile)

    def tearDown(self):
        pass

        #if os.path.exists(imgfile):
        #    os.remove(imgfile)

    def _default_assert(self, retval):
        pass
        #self.assertEqual(retval, 0)
        #self.assertTrue(os.path.exists(imgfile))

    def test_build(self):
        pass
        #argv = self.argv + [
        #    "--figure", "'test'@suptitle",
        #]

        #retval, forward = self.perform_test(matplot, argv=argv)

        #self._default_assert(retval)

test_classes = (TaskLangLabTests,)
