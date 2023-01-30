# -*- coding: utf-8 -*-

# Copyright © Educacode.

from typing import List

from pydantic_educacode.model import ApiModel


class ApiUserModel(ApiModel):
    name: str
    id: int


class ProfileResponse(ApiModel):
    user: ApiUserModel
