# Copyright (c) 2015 Robert Collins <robertc@robertcollins.net>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import doctest
import os

from testscenarios import generate_scenarios

def load_tests(loader, tests, pattern):
    this_dir = os.path.dirname(__file__)
    tests.addTests(loader.discover(start_dir=this_dir, pattern=pattern))
    doctest.set_unittest_reportflags(doctest.REPORT_ONLY_FIRST_FAILURE)
    tests.addTest(
        doctest.DocFileSuite("../../README.rst", optionflags=doctest.ELLIPSIS))
    return loader.suiteClass(generate_scenarios(tests))
