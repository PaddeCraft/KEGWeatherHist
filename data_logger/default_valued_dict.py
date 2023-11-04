from typing import Any


class DefaultValuedDict:
    __data = {}

    def __init__(self, data: dict, default_value: any) -> None:
        if type(data) == dict:
            self.__data = data
        else:
            self.__data = {}

        self.default_value = default_value

    def __getitem__(self, __name: str) -> Any:
        if __name in self.__data:
            return self.__getattribute__(__name)
        return self.default_value

    def __setitem__(self, __name: str, __value: Any) -> None:
        self.__data[__name] = __value

    def get(self, __name):
        return self.__getattribute__(__name)
