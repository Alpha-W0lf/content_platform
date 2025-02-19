from typing import List, Optional


def unformatted_function(x: int, y: Optional[str] = "test") -> List[int]:
    """This function is intentionally unformatted to test our tools."""
    unused_var = "test"  # noqa: F841
    return [x for x in range(10)]  # This has formatting and type issues


def another_function(param: int) -> int:
    return param + 1


if __name__ == "__main__":
    result = unformatted_function(42)
    print(result)
