# -*- coding: utf-8 -*-
import werkzeug
from odoo import http
from pydantic import BaseModel


class MyObject(BaseModel):
    name: str
    age: int


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
    def api(self, data: MyObject) -> str:
        """TEST DOCSTRING"""
        print("---------DATAOBJECT----------------", data)
        # print("---------KW----------------", kw)

        return {"id": http.request.session.uid}

    @http.route("/test", type="http", auth="public", methods=["GET", "POST"])
    def test(self, **kw):
        rv = http.request.env["api_route.open_api"].get_json()

        return str(rv)
