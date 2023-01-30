# -*- coding: utf-8 -*-

# Copyright © Educacode.

from pydantic_educacode.model import ApiModel


class PingResponse(ApiModel):
    csrf: str
    user: int
