# -*- coding: utf-8 -*-

# Copyright © Educacode.

from typing import List, Optional

from pydantic import validator
from pydantic_educacode.model import ApiModel


class Todo(ApiModel):
    id: int
    name: str
    content: str
    update_date: str

    @validator("update_date", pre=True)
    def parse_pushdate(cls, value):
        try:
            res = value.strftime("%d/%m/%Y")
        except:
            res = None
        return res


class TodoCreate(ApiModel):
    name: str
    content: str


class TodoListResponse(ApiModel):
    todos: List[Todo]


class TodoPatch(ApiModel):
    name: Optional[str] = None
    content: Optional[str] = None
