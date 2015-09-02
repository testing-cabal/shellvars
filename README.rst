:Homepage: `Shellvars Homepage`_
:Download: `Shellvars on PyPI`_
:Documentation: `Shellvars Docs`_
:License: `MIT License`_
:Support: `Mailing list (testing-in-python@lists.idyll.org)
 <http://lists.idyll.org/listinfo/testing-in-python>`_
:Issue tracker: `Github Issues
 <https://github.com/testing-cabal/shellvars/issues>`_
:Build status:
  .. image:: https://travis-ci.org/testing-cabal/shellvars.svg?branch=master
      :target: https://travis-ci.org/testing-cabal/shellvars

.. _Shellvars Homepage: https://github.com/testing-cabal/shellvars
.. _MIT License: http://github.com/testing-cabal/shellvars/blob/master/LICENSE.txt
.. _Shellvars Docs: https://pypi.python.org/pypi/shellvars
.. _Shellvars on PyPI: http://pypi.python.org/pypi/shellvars

=========
Shellvars
=========

A Python interpreter for shell variable expressions.

shellvars supports Python 2.6 and up, and should support Jython etc as well.

The following expressions are supported:

* ``$NAME``
* ``${NAME}``
* ``${NAME:-REPLACEMENT}``
* ``${NAME-REPLACEMENT}``
* ``${NAME:=REPLACEMENT}``
* ``${NAME=REPLACEMENT}``
* ``${NAME:?[ERRORMSG]}``
* ``${NAME?[ERRORMSG]}``
* ``${NAME:+REPLACEMENT}``
* ``${NAME+REPLACEMENT}``

Recursive expressions are supported too. For instance::

  >>> from shellvars import evaluate
  >>> evaluate('${foo:-${bar:=baz}}', {})
  ('baz', {'bar': 'baz'})

For details on shell variable syntax, consult your shell or Posix
documentation.

Usage
=====

To evaluate an expression call ``evaluate`` with the expression and any
variables you want available to the expression. Variables keys and values must
both be strings.  Variables that are missing from your variable dict are
considered 'unset' in shell terms.

The return is an evaluated string and any variable assignments performed
by the expression.

Preserving unset expressions
++++++++++++++++++++++++++++

shellvars has a special mode where expressions that are for unset variables
are preserved rather than evaluated. This permits passing them onto a real
shell to interpret without needing special quoting from the user. For
instance::

 >>> from shellvars import SKIP
 >>> evaluate('$foo $bar', {'foo': 'baz'}, absent=SKIP)
 ('baz $bar', {})


Installation
============

Use pip to install::

  pip install shellvars

Development
===========

Install the test dependencies via pip::

  pip install .[test]

Push up changes as PR's to the GitHub `repository 
<https://github.com/testing-cabal/shellvars>`_.

Bug tracker
===========

Use the GitHub `issue tracker
<https://github.com/testing-cabal/shellvars/issues>`_.

Releasing
=========

Use semver for version decisions.

To release:

1. Tag the repo e.g. 1.2.3

2. Build a signed sdist and wheel

3. Upload to PyPI

Copyright
=========

Copyright (c) 2015 Robert Collins <robertc@robertcollins.net>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
