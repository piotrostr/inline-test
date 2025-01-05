import sys
import inspect
import importlib.util
import argparse
from typing import Any, Tuple, List, Optional
from pathlib import Path


class TestResult:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.failed_tests = []


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
    parser.add_argument("files", nargs="+", help="Python files to test")
    parser.add_argument("--tag", help="Only run tests with this tag")

    args = parser.parse_args()

    total_results = TestResult()

    for file_path in args.files:
        if not Path(file_path).exists():
            print(f"File not found: {file_path}")
            continue

        print(f"\nRunning tests in {file_path}")
        print("=" * 40)

        module = load_module(file_path)
        results = run_tests(module, args.tag)

        total_results.passed += results.passed
        total_results.failed += results.failed
        total_results.failed_tests.extend(results.failed_tests)

    print("\nTest Summary")
    print("=" * 40)
    print(f"Total: {total_results.passed + total_results.failed}")
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
