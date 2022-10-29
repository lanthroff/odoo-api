# -*- coding: utf-8 -*-

# Copyright © Educacode.

from odoo import http

from ..schemas.myobject import MyObject, MyObjectResponse


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
        print(data.pretty(h="H", v="V"))
        return MyObjectResponse(id=http.request.session.uid)
