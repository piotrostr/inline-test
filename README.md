# inline-tests

Rust-like inline tests for Python. Write and run tests right next to your code!

## Installation

```bash
pip install inline-tests
```

## Usage

In your Python files:

```python
from inline_tests.decorators import test, before_each, after_each

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
# Run all tests in current directory
run-tests

# Run specific files
run-tests file1.py file2.py

# Run tests with specific tag
run-tests --tag math

# Run tests in specific directory
run-tests --path /path/to/project
```
