# -*- coding: utf-8 -*-

# Copyright © Educacode.

from ....api_route.models.api_model import ApiModel


class PingResponse(ApiModel):
    csrf: str
    user: int
