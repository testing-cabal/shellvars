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

from hypothesis import given
# To debug hypothesis
# from hypothesis import Settings, Verbosity
# Settings.default.verbosity = Verbosity.verbose
import hypothesis.strategies as st
from testtools import TestCase
from testtools.matchers import Equals

from shellvars import evaluate, EMPTY, SKIP


class TestEvaluate(TestCase):

    scenarios = [
        ('absent-empty', {'absent': EMPTY}),
        ('absent-skip', {'absent': SKIP}),
        ]

    def test_nothing(self):
        self.expectThat(
            evaluate("", {}, self.absent),
            Equals(""))

    def test_simple(self):
        self.expectThat(
            evaluate("pre $BAR post", {"BAR": "quux"}, self.absent),
            Equals("pre quux post"))

    @given(st.text())
    def test_hypothesis(self, a_string):
        evaluate(a_string, {}, self.absent)

    def test_simple_absent(self):
        if self.absent is EMPTY:
            result = ""
        else:
            result = "$BAR"
        self.expectThat(
            evaluate("pre $BAR post", {}, self.absent),
            Equals("pre " + result + " post"))

