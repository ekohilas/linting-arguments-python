"""Category: arity & argument ordering (call axes C3/C4).

Varies argument count relative to the signature (exact, defaults-omitted,
too-few, too-many-positional, unexpected-keyword, duplicate positional+keyword,
absorbed-by-varargs/kwargs) and ordering (canonical, keywords reordered,
positional-then-keyword, illegal positional-after-keyword). Runtime-error cases
tag `validity: runtime_error`; syntax-error cases tag `validity: syntax_error`.
"""

from catalog._schema import Case

CATEGORY = "arity_and_ordering"

CASES = []
