# -*- coding: utf-8 -*-

# Copyright © Educacode.

from typing import List

from ....api_route.models.api_model import ApiModel


class ApiUserModel(ApiModel):
    name: str
    id: int


class ProfileResponse(ApiModel):
    user: ApiUserModel
