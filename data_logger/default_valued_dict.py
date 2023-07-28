from typing import Any


class DefaultValuedDict:
    def __init__(self, data: dict, default_value: any) -> None:
        if type(data) == dict:
            self.data = data
        else:
            self.data = {}

        self.default_value = default_value

    def __getattribute__(self, __name: str) -> Any:
        if __name in self.data:
            return self.__getattribute__(__name)
        return self.default_value

    def __setattr__(self, __name: str, __value: Any) -> None:
        self.data[__name] = __value

    def get(self, __name):
        return self.__getattribute__(__name)
