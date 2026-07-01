# linting-arguments-python
Provides linting rules around function arguments in Python

## Getting Started

Use [`uv`](https://docs.astral.sh/uv/)

## Run Tests

```shell
uv run pytest test/tests.py
uv run pytest test/test_keyword_only.py
```

## Keyword-only arguments rule

`linting_arguments_python.keyword_only_checker` flags function definitions that
do not force their arguments to be keyword-only with a `*` marker. Load it as a
pylint plugin:

```shell
uv run pylint --load-plugins=linting_arguments_python.keyword_only_checker your_module.py
```

By default every argument must be keyword-only (`def f(*, a, b)`), and calling
`f(1)` positionally is reported as `missing-keyword-only-marker` (`W9011`).

### Options

- `--max-positional-arguments=<int>` (default `0`): the number of leading
  positional arguments allowed before a `*` marker is required. `0` means every
  argument must be keyword-only; `1` allows a single leading positional argument;
  and so on.
- `--check-lambdas=<y or n>` (default `n`): also enforce the rule on `lambda`
  expressions.

`self`/`cls` on methods and classmethods are never counted. Protocol methods
that Python must invoke positionally (operator dunders such as `__eq__` and
`__getitem__`, and property `@x.setter`/`@x.deleter`) are exempt. `*args` is
ignored, since it cannot be made keyword-only.
