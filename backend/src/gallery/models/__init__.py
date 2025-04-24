from typing import Type,  Protocol


class HasTable[T](Protocol):
    _TABLE: Type[T] = NotImplemented
