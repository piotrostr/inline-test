# intest

Rust-like inline tests for Python. Write and run tests right next to your code!

Haven't tested this on large projects, but it provides the amazing feature of
rust which is a single file with its tests

Surprised this didn't exist prior

No async, no fixtures, no fancy stuff

## Installation

```bash
pip install intest
```

## Usage

In your Python files:

```python
from intest.decorators import test, before_each, after_each

def add(a: int, b: int) -> int:
    return a + b

@test
def test_add():
    assert add(2, 2) == 4

@test(tag="math")
def test_add_negative():
    assert add(-2, -2) == -4
```

Run tests:

```bash
# Run all tests in project
intest

# Run specific files
intest file1.py file2.py

# Run tests with specific tag
intest --tag math

# Run tests in specific directory
intest --path /path/to/project
```
