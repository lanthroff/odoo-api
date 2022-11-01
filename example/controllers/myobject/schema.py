# -*- coding: utf-8 -*-

# Copyright © Educacode.

from ....api_route.models.api_model import ApiModel


class MyObject(ApiModel):
    name: str
    age: int


class MyObjectResponse(ApiModel):
    id: int
