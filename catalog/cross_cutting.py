"""Category: cross-cutting combinations (creative overflow).

Cases that combine axes or don't cleanly belong to one file: redundant keywords
(`f(x=x)`), parameters shadowing builtins (`def f(list): ...`), reserved-ish
parameter names (`type`, `id`, `input`), passing `self` explicitly
(`Class.method(instance, arg)`), pre-bound `functools.partial` positionals,
overload-dispatch ambiguity, keyword colliding with a `**kwargs` key, and the
argument-name-vs-parameter-name mismatch that motivates the talk's warning rule.
"""

from catalog._schema import Case

CATEGORY = "cross_cutting"

CASES = []
