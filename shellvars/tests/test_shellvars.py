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
from testscenarios import multiply_scenarios
from testtools import TestCase
from testtools.matchers import Equals, Raises, raises, Matcher

from shellvars import (
    EMPTY,
    EvaluationError,
    SKIP,
    _Expression,
    _Literal,
    _SimpleExpression,
    _grammar,
    evaluate,
    )


class Eval(Matcher):
    """Evaluate the matchee then pass to the decorated matcher."""

    def __init__(self, matcher):
        self.matcher = matcher

    def match(self, something):
        return self.matcher.match(something())

    def __str__(self):
        return "Eval(%(matcher)s)" % {'matcher': self.matcher}


class TestEvaluate(TestCase):

    scenarios = [
        ('absent-empty', {'absent': EMPTY}),
        ('absent-skip', {'absent': SKIP}),
        ]

    def test_nothing(self):
        self.expectThat(
            evaluate("", {}, self.absent),
            Equals(("", {})))

    def test_simple(self):
        self.expectThat(
            evaluate("pre $BAR post", {"BAR": "quux"}, self.absent),
            Equals(("pre quux post", {})))

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
            Equals(("pre " + result + " post", {})))

    def test_braces(self):
        self.expectThat(
            evaluate("pre ${BAR} post", {"BAR": "quux"}, self.absent),
            Equals(("pre quux post", {})))
        self.expectThat(
            evaluate("pre ${BAR} mid ${BAR} post", {"BAR": "quux"}, self.absent),
            Equals(("pre quux mid quux post", {})))


class TestFormats(TestCase):

    scenarios = multiply_scenarios([
        ('absent-empty', {'absent': EMPTY}),
        ('absent-skip', {'absent': SKIP}),
        ], [
        ('colon', {'colon': ':'}),
        ('nocolon', {'colon': ''}),
        ])

    def cons(self, param, op, word):
        return '${%(param)s%(colon)s%(op)s%(word)s}' % {
            'param': param,
            'colon': self.colon,
            'op': op,
            'word': word,
            }

    def test_default_values(self):
        expr = "pre " + self.cons('bar', '-', '${foo}') +" post"
        self.expectThat(
            evaluate(expr, {'bar': 'quux', 'foo': 'baz'}, self.absent),
            Equals(('pre quux post', {})))
        if self.colon:
            expected = Equals(('pre baz post', {}))
        else:
            expected = Equals(('pre  post', {}))
        self.expectThat(
            evaluate(expr, {'bar': '', 'foo': 'baz'}, self.absent),
            expected)
        if self.absent is EMPTY:
            expected = Equals(('pre baz post', {}))
        else:
            expected = Equals((expr, {}))
        self.expectThat(
            evaluate(expr, {'foo': 'baz'}, self.absent),
            expected)

    def test_assign_default_values(self):
        expr = "pre " + self.cons('bar', '=', '${foo}') +" post"
        self.expectThat(
            evaluate(expr, {'bar': 'quux', 'foo': 'baz'}, self.absent),
            Equals(('pre quux post', {'bar': 'quux'})))
        if self.colon:
            expected = Equals(('pre baz post', {'bar': 'baz'}))
        else:
            expected = Equals(('pre  post', {'bar': ''}))
        self.expectThat(
            evaluate(expr, {'bar': '', 'foo': 'baz'}, self.absent),
            expected)
        if self.absent is EMPTY:
            expected = Equals(('pre baz post', {'bar': 'baz'}))
        else:
            expected = Equals((expr, {}))
        self.expectThat(
            evaluate(expr, {'foo': 'baz'}, self.absent),
            expected)
        # Nested assignments bubble up.
        inner = self.cons('bar', '=', 'baz')
        outer = self.cons('foo', '-', inner)
        if self.absent is EMPTY:
            expected = Equals(('baz', {'bar': 'baz'}))
        else:
            expected = Equals((outer, {}))
        self.expectThat(
            evaluate(outer, {}, self.absent),
            expected)
        # Assignments are honoured inline
        first = self.cons('foo', '=', 'bar')
        second = self.cons('foo', '-', 'baz')
        expr = first + second
        if self.absent is EMPTY:
            expected = Equals(('barbar', {'foo': 'bar'}))
        else:
            expected = Equals((expr, {}))
        self.expectThat(
            evaluate(expr, {}, self.absent),
            expected)

    def test_error_implicit(self):
        expr = "pre " + self.cons('bar', '?', '') + " post"
        self.expectThat(
            evaluate(expr, {'bar': 'quux'}, self.absent),
            Equals(('pre quux post', {})))
        if self.colon:
            expected = raises(EvaluationError("Variable 'bar' null or unset."))
        else:
            expected = Eval(Equals(('pre  post', {})))
        self.expectThat(
            lambda: evaluate(expr, {'bar': ''}, self.absent),
            expected)
        if self.absent is EMPTY:
            expected = raises(EvaluationError("Variable 'bar' null or unset."))
        else:
            expected = Eval(Equals((expr, {})))
        self.expectThat(
            lambda: evaluate(expr, {}, self.absent),
            expected)

    def test_error_explicit(self):
        expr = "pre " + self.cons('bar', '?', '$foo') + " post"
        self.expectThat(
            evaluate(expr, {'bar': 'quux'}, self.absent),
            Equals(('pre quux post', {})))
        if self.colon:
            expected = raises(EvaluationError("baz"))
        else:
            expected = Eval(Equals(('pre  post', {})))
        self.expectThat(
            lambda: evaluate(expr, {'bar': '', 'foo': 'baz'}, self.absent),
            expected)
        if self.absent is EMPTY:
            expected = raises(EvaluationError("baz"))
        else:
            expected = Eval(Equals((expr, {})))
        self.expectThat(
            lambda: evaluate(expr, {'foo': 'baz'}, self.absent),
            expected)

    def test_alternative_values(self):
        expr = "pre " + self.cons('bar', '+', '${foo}') +" post"
        self.expectThat(
            evaluate(expr, {'bar': 'quux', 'foo': 'baz'}, self.absent),
            Equals(('pre baz post', {})))
        if self.colon:
            expected = Equals(('pre  post', {}))
        else:
            expected = Equals(('pre baz post', {}))
        self.expectThat(
            evaluate(expr, {'bar': '', 'foo': 'baz'}, self.absent),
            expected)
        if self.absent is EMPTY:
            expected = Equals(('pre  post', {}))
        else:
            expected = Equals((expr, {}))
        self.expectThat(
            evaluate(expr, {'foo': 'baz'}, self.absent),
            expected)


class TestGrammar(TestCase):

    def test_name(self):
        for name in (
            'a', '_', 'A', 'ba', 'b_', 'b1', 'bA', '_a', '_1', '_A', 'Aa',
            'A_', 'A0', 'adsd2343aweawe_'):
            g = _grammar(name)
            self.expectThat(g.name(), Equals(name))
        for notname in ('1', ' ', '{'):
            g = _grammar(notname)
            self.expectThat(g.name, Raises())

    def test_expr(self):
        for text, node in (
            ('$a', _SimpleExpression('a', '$a')),
            ('$a1', _SimpleExpression('a1', '$a1')),
            ('${ab}', _SimpleExpression('ab', '${ab}')),
            ('${ab:-}', 
                _Expression('ab', ':', '-', [], '${ab:-}')),
            ('${ab:-${foo}}', 
                _Expression('ab', ':', '-', [_SimpleExpression('foo', '${foo}')],
                            '${ab:-${foo}}')),
            ('${ab:-${cd:-${foo}}}', 
                _Expression(
                    'ab', ':', '-',
                    [_Expression(
                        'cd', ':', '-',
                        [_SimpleExpression('foo', '${foo}')],
                        '${cd:-${foo}}'),
                        ],
                    '${ab:-${cd:-${foo}}}')),
            ):
            g = _grammar(text)
            self.expectThat(g.expr(), Equals(node))
        for notname in ('1', ' ', '{'):
            g = _grammar(notname)
            self.expectThat(g.expr, Raises())

    def test_notexpr(self):
        for text, node in (
            ('1', _Literal('1')),
            ('a', _Literal('a')),
            ('a1', _Literal('a1')),
            ('$', _Literal('$')),
            ('$1', _Literal('$1')),
            ):
            g = _grammar(text)
            self.expectThat(g.notexpr(), Equals(node))
        for expr in ('$a', ):
            g = _grammar(expr)
            self.expectThat(g.notexpr, Raises())

    def test_string(self):
        for text, nodes in (
            ('', []),
            ('1', [_Literal('1')]),
            ('$1', [_Literal('$1')]),
            ('1$a', [_Literal('1'), _SimpleExpression('a', '$a')]),
            ('1$a$b', [
                _Literal('1'), _SimpleExpression('a', '$a'),
                _SimpleExpression('b', '$b')]),
            ('1$a2$b3', [
                _Literal('1'), _SimpleExpression('a2', '$a2'),
                _SimpleExpression('b3', '$b3')]),
            ('1$a 2$b 3', [
                _Literal('1'), _SimpleExpression('a', '$a'), _Literal(' 2'),
                _SimpleExpression('b', '$b'),
                _Literal(' 3')]),
            ('1${ab:-${cd:-${foo}}}2', [
                _Literal('1'),
                _Expression(
                    'ab', ':', '-',
                    [_Expression(
                        'cd', ':', '-',
                        [_SimpleExpression('foo', '${foo}')],
                        '${cd:-${foo}}'),
                        ],
                    '${ab:-${cd:-${foo}}}'),
                _Literal('2'),
                ]),
            ):
            g = _grammar(text)
            self.expectThat(g.string(), Equals(nodes))
