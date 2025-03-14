from typing import Callable, TypeVar, ParamSpec

T = TypeVar('T')
P = ParamSpec('P')


def my_decorator(func: Callable[P, T]) -> Callable[P, str]:
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> str:
        print("Before the function call")
        result = func(*args, **kwargs)
        print("After the function call")
        return result
    return wrapper


@my_decorator
def example_function(x: int, y: int) -> int:
    return x + y


if __name__ == "__main__":
    result = example_function(3, 4)
    print(f"Result: {result}")
