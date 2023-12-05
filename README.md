# quantecon-book-networks

Python Package for https://networks.quantecon.org (Economic Networks)

# Releases

# 2023-Dec-06: v1.1

DEPS: Add POTS as a dependency to support the lectures and enable automatic installation of dependencies

# 2023-Nov-20: v1.0

This is the first `v1` release to support the publication of the book

## Package Builder

This package uses [flit]() to build and publish updates to PyPI

To update the package:

1. Make the necessary updates to `main` (via PR or push)
2. Use `flit install` to install it for local testing
3. To publish use `flit publish`

> :warning: You will need to have mantainer priviledges 
> on PyPI for `quantecon_book_networks` package.

The configuration for `flit` is found in `pyproject.toml`