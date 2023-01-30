# -*- coding: utf-8 -*-

# Copyright © Educacode.

from pydantic_educacode.model import ApiModel


class LoginRequest(ApiModel):
    login: str
    password: str


class LoginResponse(ApiModel):
    success: bool
    csrf: str
