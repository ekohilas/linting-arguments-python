"""Category: definition source & inferability (environment axes E1/E2/E3).

Varies where the callable comes from and whether astroid can infer its
definition: same-module (editable), same-project, standard library (not
editable), third-party (not editable), C builtins with no introspectable
signature (`len`, `print`), dynamically generated / uninferable, stub-only.
Also inferability (full/partial/uninferable) and multiplicity of inference.

This axis governs whether an auto-fix rule is even *allowed* to act (you cannot
edit stdlib), and mirrors the `next(func.infer())` boundary in
`my_plugin.check_call_arguments`.
"""

from catalog._schema import Case

CATEGORY = "source_and_inferability"

CASES = []
