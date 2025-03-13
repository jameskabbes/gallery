from typing import Callable, TypeVar

T = TypeVar('T')


def my_decorator(func: Callable[..., T]) -> Callable[..., T]:
    def wrapper(*args, **kwargs) -> T:
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
