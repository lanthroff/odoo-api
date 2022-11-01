# -*- coding: utf-8 -*-

# Copyright © Educacode.

from pydantic import BaseModel, Extra


def data_to_string(data, indent=1):
    if type(data) == dict:
        return "\n" + "\n".join(
            [
                f"{key}: {data_to_string(data[key], indent=indent+1)}"
                if (type(data[key]) == dict or type(data[key]) == list)
                else f"{'   '*indent}{key}: {data[key]}"
                for key in data
            ]
        )
    if type(data) == list:
        return "\n" + "\n".join(
            [
                data_to_string(item, indent=indent + 1)
                if (type(item) == dict or type(item) == list)
                else f"{'   '*indent}{item}"
                for item in data
            ]
        )


class ApiModel(BaseModel):
    def __str__(self):
        return f"{self.__class__.__name__}({', '.join([ f'{key}={self.__dict__.get(key)}' for key in self.__dict__])})"

    def pretty(self, h="*", v="|"):
        """
        Do not disturb
        """
        class_name = self.__class__.__name__
        body = data_to_string(self.dict()) if self else "None"
        # Add borders to body
        width = max([len(class_name) + 12] + [len(item) for item in body.split("\n")])
        if (width - len(class_name)) % 2:
            width += 1
        header = (
            f"{h * (((width - len(class_name)) // 2) - 1 ) } {class_name} {h * (((width - len(self.__class__.__name__)) // 2) - 1 ) }"
            + "\n"
            + f"{v}{' ' * (width - 2)}{v}"
        )
        footer = f"{v}{' ' * (width - 2)}{v}" + "\n" + h * width + "\n"
        return "\n" + header + body + "\n" + footer

        h = h[0] if len(h) > 1 else h
        v = v[0] if len(v) > 1 else v
        width = max(
            [len(self.__class__.__name__) + 12]
            + [len(f"{key}: {getattr(self, key)}") + 4 for key in self.__dict__]
        )
        if (width - len(self.__class__.__name__)) % 2:
            width += 1

        header = (
            f"{h * (((width - len(self.__class__.__name__)) // 2) - 1 ) } {self.__class__.__name__} {h * (((width - len(self.__class__.__name__)) // 2) - 1 ) }"
            + "\n"
            + f"{v}{' ' * (width - 2)}{v}"
            + "\n"
        )
        footer = f"{v}{' ' * (width - 2)}{v}" + "\n" + h * width + "\n"
        result = "\n"
        result += header
        for key in self.__dict__:
            data = f"{key}: {getattr(self, key)}"
            result += f"{v} {data}{' ' * (width - len(data) - 3)}{v}" + "\n"
        result += footer
        return result

    class Config:
        extra = Extra.forbid
