# linting-arguments-python
Provides linting rules around function arguments in Python

## Getting Started

Use [`uv`](https://docs.astral.sh/uv/)

## Run Tests

```shell
uv run pytest test/tests.py
```

## `argument-name-mismatch`

Flags a positional argument when the variable passed is a plain name that does
not match the parameter it is bound to. A mismatch is a common sign that
arguments were accidentally swapped.

```python
def transfer(source, destination): ...

transfer(source, destination)       # ok:   names line up
transfer(destination, source)       # W9101: arguments look swapped
transfer(source=x, destination=y)   # ok:   keywords are explicit
```

Only positional arguments that are plain variable references are checked;
keyword arguments, literals, attributes, and other expressions are left alone.
The rule resolves plain functions, methods, class methods, static methods,
lambdas, and class constructors.

Enable it as a pylint plugin:

```shell
uv run pylint --load-plugins=linting_arguments_python.argument_name_checker \
  --enable=argument-name-mismatch your_module.py
```

Run its tests with:

```shell
uv run pytest test/test_argument_name_checker.py
```
