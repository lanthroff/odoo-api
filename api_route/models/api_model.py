# -*- coding: utf-8 -*-

# Copyright © Educacode.

import json

from pydantic import BaseModel, Extra


class ApiModel(BaseModel):
    def __str__(self):
        return f"{self.__class__.__name__}({', '.join([ f'{key}={self.__dict__.get(key)}' for key in self.__dict__])})"

    def pretty(self):
        if self is None:
            return None

        class_name = self.__class__.__name__
        body = json.dumps(self.dict(), indent=2)
        width = max([len(class_name) + 12] + [len(item) for item in body.split("\n")])
        if (width - len(class_name)) % 2:
            width += 1

        header = f"{'*'* (((width - len(class_name))//2)-1)} {class_name} {'*'* (((width - len(class_name))//2)-1)}"
        footer = "*" * width
        return "\n{header}\n{body}\n{footer}\n".format(
            header=header, body=body, footer=footer
        )

    class Config:
        extra = Extra.forbid
