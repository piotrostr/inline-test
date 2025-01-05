import sys
import inspect
import importlib.util
import argparse
from typing import Any, List, Optional, Iterator
from pathlib import Path
import ast


class TestResult:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.failed_tests = []


def contains_test_decorator(file_path: Path) -> bool:
    """Check if a file contains the @test decorator without importing it."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read())

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                for decorator in node.decorator_list:
                    # Check for plain @test
                    if isinstance(decorator, ast.Name) and decorator.id == "test":
                        return True
                    # Check for @test() or @test(tag="something")
                    if isinstance(decorator, ast.Call):
                        if (
                            isinstance(decorator.func, ast.Name)
                            and decorator.func.id == "test"
                        ):
                            return True
        return False
    except Exception as e:
        print(f"Warning: Could not parse {file_path}: {e}")
        return False


def find_test_files(start_path: Path = Path.cwd()) -> Iterator[Path]:
    """Find all Python files containing test decorators."""
    for path in start_path.rglob("*.py"):
        # Skip common test directories and virtual environments
        if any(
            part.startswith((".", "venv", "env", "__pycache__")) for part in path.parts
        ):
            continue

        if contains_test_decorator(path):
            yield path


def load_module(file_path: str) -> Any:
    spec = importlib.util.spec_from_file_location("module", file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_tests(module: Any, tag: Optional[str] = None) -> TestResult:
    result = TestResult()

    # Get setup/teardown functions
    before_each = next(
        (
            obj
            for _, obj in inspect.getmembers(module)
            if inspect.isfunction(obj) and hasattr(obj, "_is_before_each")
        ),
        None,
    )

    after_each = next(
        (
            obj
            for _, obj in inspect.getmembers(module)
            if inspect.isfunction(obj) and hasattr(obj, "_is_after_each")
        ),
        None,
    )

    # Get test functions
    test_functions = [
        obj
        for _, obj in inspect.getmembers(module)
        if inspect.isfunction(obj)
        and hasattr(obj, "_is_test")
        and (tag is None or getattr(obj, "_tag", None) == tag)
    ]

    for test_func in test_functions:
        try:
            if before_each:
                before_each()

            test_func()
            print(f"✅ {test_func.__name__} passed")
            result.passed += 1

        except AssertionError as e:
            print(f"❌ {test_func.__name__} failed: {str(e)}")
            result.failed += 1
            result.failed_tests.append((test_func.__name__, str(e)))
        except Exception as e:
            print(f"❌ {test_func.__name__} failed with exception: {str(e)}")
            result.failed += 1
            result.failed_tests.append((test_func.__name__, str(e)))
        finally:
            if after_each:
                after_each()

    return result


def main():
    parser = argparse.ArgumentParser(description="Run inline tests in Python files")
    parser.add_argument("files", nargs="*", help="Python files to test (optional)")
    parser.add_argument("--tag", help="Only run tests with this tag")
    parser.add_argument(
        "--path",
        type=Path,
        default=Path.cwd(),
        help="Path to scan for test files (default: current directory)",
    )

    args = parser.parse_args()

    files_to_test = []

    if args.files:
        # Use specified files
        files_to_test = [Path(f) for f in args.files]
    else:
        # Auto-discover files with tests
        print("No files specified, scanning for files with tests...")
        files_to_test = list(find_test_files(args.path))
        if not files_to_test:
            print("No files with tests found!")
            return
        print(f"Found {len(files_to_test)} files with tests")

    total_results = TestResult()

    for file_path in files_to_test:
        if not file_path.exists():
            print(f"File not found: {file_path}")
            continue

        print(f"\nRunning tests in {file_path}")
        print("=" * 40)

        try:
            module = load_module(str(file_path))
            results = run_tests(module, args.tag)

            total_results.passed += results.passed
            total_results.failed += results.failed
            total_results.failed_tests.extend(results.failed_tests)
        except Exception as e:
            print(f"Failed to run tests in {file_path}: {str(e)}")

    print("\nTest Summary")
    print("=" * 40)
    print(f"Files tested: {len(files_to_test)}")
    print(f"Total tests: {total_results.passed + total_results.failed}")
    print(f"Passed: {total_results.passed}")
    print(f"Failed: {total_results.failed}")

    if total_results.failed_tests:
        print("\nFailed Tests:")
        for name, error in total_results.failed_tests:
            print(f"  {name}: {error}")

    if total_results.failed > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
