# -*- coding: utf-8 -*-
from odoo import http
from pydantic import BaseModel


class ApiModel(BaseModel):
    def __str__(self):
        return f"{self.__class__.__name__}({', '.join([ f'{key}={self.__dict__.get(key)}' for key in self.__dict__])})"


class MyObject(ApiModel):
    name: str
    age: int


class MyObjectResponse(ApiModel):
    id: int


class Example(http.Controller):
    @http.route("/profile", type="api", auth="user", methods=["GET", "POST"])
    def profile(self, **kw):
        owned_cars = http.request.env["example.cars"].search(
            [("owner", "=", http.request.session.uid)]
        )
        return {
            "user": {
                "id": http.request.env.user.id,
                "name": http.request.env.user.name,
            },
            "cars": [el.name for el in owned_cars],
        }

    @http.route("/api", type="api", auth="public", methods=["GET", "POST"])
    def api(self, data: MyObject = None, **kw) -> MyObjectResponse:
        """TEST DOCSTRING"""
        print(data)
        print("---------KW----------------", kw)

        return {"id": http.request.session.uid}

    @http.route("/docs", type="http", auth="public", methods=["GET", "POST"])
    def docs(self, **kw):
        return http.request.env["api_route.open_api"].get_json()
