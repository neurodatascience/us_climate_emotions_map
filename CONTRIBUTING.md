# CONTRIBUTING

## tox

[Tox](https://tox.wiki/en) is set
to facilitate testing and managing environments during development
and ensure that the same commands can easily be run locally and in CI.

Install it with:

```bash
pip install -r requirements_dev.txt
```

You can set up certain environment or run certain command by calling ``tox``.

Calling ``tox`` with no extra argument will simply run
all the default commands defined in the tox configuration (``tox.ini``).
In our case it will run all our formatting tools by using [`pre-commit`](#pre-commit)

Use ``tox list`` to view all environment descriptions.

Use ``tox run`` to run a specific environment.

Example

```bash
tox run -e lint
```

Some environments allow passing extra argument:

```bash
# only run black
tox run -e lint -- black
```

## Code style

We use:
- [black](https://black.readthedocs.io/en/stable/) for python code formatting
- [isort](https://pycqa.github.io/isort/) for sorting of python imports
- [flake8](https://flake8.pycqa.org/en/latest/) with [flake8-bugbear](https://github.com/PyCQA/flake8-bugbear) for linting
- [codespell](https://github.com/codespell-project/codespell) for spellchecking

### Pre-commit

We use [pre-commit](https://pre-commit.com)
to run a set of linters and autoformatters on the codebase
and ensure code style compliance at commit time.

You can easily run it by relying on [tox](#tox) and type:

```bash
tox
```

Pre-commit will then run all those hooks on the files you have staged for commit.
Note that while several hooks will auto-fix files when they have failed the checks
(meaning you just need to stage the edited files),
for others, if the hooks fail you may have to edit some files manually before staging them again.

### To know more about pre-commit

- official documentation: https://pre-commit.com/

## Updating requirements

If you need to add new dependencies, add them to the `requirements.in` file
and then run

```bash
tox run -e update_dependencies
```

to update the content of the `requirements.txt`.
