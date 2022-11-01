# -*- coding: utf-8 -*-

# Copyright © Educacode.

from ....api_route.models.api_model import ApiModel


class LoginRequest(ApiModel):
    login: str
    password: str


class LoginResponse(ApiModel):
    success: bool
    csrf: str
