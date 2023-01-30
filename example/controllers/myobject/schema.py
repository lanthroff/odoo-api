# -*- coding: utf-8 -*-

# Copyright © Educacode.

from pydantic_educacode.model import ApiModel


class MyObject(ApiModel):
    name: str
    age: int


class MyObjectResponse(ApiModel):
    id: int
