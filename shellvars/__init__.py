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

"""Evaluate shell variable expressions."""

__all__ = ['evaluate', 'EMPTY', 'SKIP', 'EvaluationError']

from collections import namedtuple

import parsley
from parsley import makeGrammar

_Literal = namedtuple("_Literal", "value")
_SimpleExpression = namedtuple("_SimpleExpression", "name text")
_Expression = namedtuple("Expression", "name null op word text")


_grammar_text = """
name = <(letter|'_')(letterOrDigit|'_')*>
expr = simple_expr | simple_brackets | default_expr
simple_expr = <('$' name:name)>:text -> SimpleExpression(name, text)
simple_brackets = <'$' '{' name:name '}' >:text -> SimpleExpression(name, text)
default_expr = < '$' '{' name:name ':'?:null <'-'|'='|'?'|'+'>:op nestedtokens:word '}' >:text -> Expression(name, null, op, word, text)
notexpr = <(~expr anything)+>:value -> Literal(value)
string = tokens:tokens end -> tokens
tokens = (expr | notexpr)*:tokens -> tokens
nestedtokens = (expr | not_expr_no_endbrace )*:tokens -> tokens
not_expr_no_endbrace = <(~expr ~'}' anything)+>:value -> Literal(value)
"""
_grammar = makeGrammar(_grammar_text, {
    'Expression': _Expression,
    'SimpleExpression': _SimpleExpression,
    'Literal': _Literal,
    })


class _Constant:
    def __init__(self, name):
        self.name = name
    def __repr__(self):
        return 'Constant<%(name)s>' % self.__dict__
EMPTY = _Constant('EMPTY')
SKIP = _Constant('SKIP')
_sentinel = _Constant('sentinel')


class EvaluationError(Exception):
    pass


def evaluate(expression, variables, absent=EMPTY):
    """Evaluate expression with variables.

    :param expression: A shell expression to evaluate.
    :param variables: The variables available to the expression.
    :param absent: If EMPTY then variables that are not present in variables
        are treated as having the value ''. If SKIP then such variables are
        not evaluated at all.
    :return: A tuple (string, dict) where the string is the result of
        evaluating the expression, and the dict contains any variable
        assignments performed by the expression.
    """
    if absent not in (EMPTY, SKIP):
        raise ValueError("invalid value for absent %r" % (absent,))
    variables = dict(variables)
    g = _grammar(expression)
    return _evaluate(g.string(), variables, absent)

def _evaluate(nodes, variables, absent):
    output = []
    assignments = {}
    for node in nodes:
        unset = False
        if type(node) == _Literal:
            output.append(node.value)
        elif type(node) == _SimpleExpression:
            value = variables.get(node.name, _sentinel)
            if value is _sentinel:
                if absent is SKIP:
                    output.append(node.text)
                    continue
                else:
                    value = ''
            output.append(value)
        elif type(node) == _Expression:
            if node.op == '-':
                # Default
                value = variables.get(node.name, _sentinel)
                if value is _sentinel:
                    if absent is SKIP:
                        output.append(node.text)
                        continue
                    else:
                        unset = True
                if unset or not value:
                    if unset or node.null is not None:
                        value, _assign = _evaluate(node.word, variables, absent)
                        assignments.update(_assign)
                    else:
                        value = ''
                output.append(value)
            elif node.op == '=':
                # Assignment
                value = variables.get(node.name, _sentinel)
                if value is _sentinel:
                    if absent is SKIP:
                        output.append(node.text)
                        continue
                    else:
                        unset = True
                if unset or not value:
                    if unset or node.null is not None:
                        value, _assign = _evaluate(node.word, variables, absent)
                        assignments.update(_assign)
                    else:
                        value = ''
                output.append(value)
                assignments[node.name] = value
                variables[node.name] = value
            elif node.op == '?':
                # Error
                value = variables.get(node.name, _sentinel)
                if value is _sentinel:
                    if absent is SKIP:
                        output.append(node.text)
                        continue
                    else:
                        unset = True
                if unset or not value:
                    if unset or node.null is not None:
                        value, _ = _evaluate(node.word, variables, absent)
                        if value:
                            raise EvaluationError(value)
                        else:
                            raise EvaluationError(
                                "Variable '%s' null or unset." % (node.name,))
                    else:
                        value = ''
                output.append(value)
            elif node.op == '+':
                # Alternative value
                value = variables.get(node.name, _sentinel)
                if value is _sentinel:
                    if absent is SKIP:
                        output.append(node.text)
                        continue
                    else:
                        unset = True
                if unset or not value and node.null:
                    value = ''
                else:
                        value, _assign = _evaluate(node.word, variables, absent)
                        assignments.update(_assign)
                output.append(value)
            else:
                raise Exception("Unhandled operation")
        else:
            raise Exception('Unknown node type')
    return ''.join(output), assignments
