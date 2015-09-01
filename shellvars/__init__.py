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

__all__ = ['evaluate', 'EMPTY', 'SKIP']

import re


var_re = re.compile('(\$[A-Za-z_][A-Za-z0-9_]*)')

EMPTY = True
SKIP = False


def evaluate(expression, variables, absent=EMPTY):
    """Evaluate expression with variables.

    :param expression: A shell expression to evaluate.
    :param variables: The variables available to the expression.
    :param absent: If EMPTY then variables that are not present in variables
        are treated as having the value ''. If SKIP then such variables are
        not evaluated at all.
    :return: A string.
    """
    if absent not in (EMPTY, SKIP):
        raise ValueError("invalid value for absent %r" % (absent,))
    def replace(var_match):
        varname = var_match.group(0)[1:]
        if absent is SKIP and varname not in variables:
            return var_match.group(0)
        varvalue = variables.get(varname, '')
        return varvalue
    return var_re.sub(replace, expression)
