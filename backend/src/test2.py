from typing import TypeVar, ParamSpec, Concatenate, Awaitable
from functools import wraps
import asyncio
from collections.abc import Callable

T = TypeVar('T')
P = ParamSpec('P')


async def my_decorator(func: Callable[Concatenate["A", P]]) -> Callable[Concatenate["A", P], Awaitable[str]]:
    @wraps(func)
    async def wrapper(cls: "A", *args: P.args, **kwargs: P.kwargs) -> str:
        print("Before the function call")
        result = func(*args, **kwargs)
        print("After the function call")
        return result
    return wrapper


class A:

    @classmethod
    @my_decorator
    async def example_function(cls, x: int, y: int) -> int:
        return x + y


async def test():
    result = await A.example_function(3, 4)
    print(f"Result: {result}")


if __name__ == "__main__":

    asyncio.run(test())
