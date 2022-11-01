# -*- coding: utf-8 -*-

# Copyright © Educacode.

from odoo import http

from .schema import ProfileResponse


class ApiProfileController(http.Controller):
    @http.route("/profile", type="api", auth="user", methods=["GET", "POST"])
    def profile(self, **kw) -> ProfileResponse:
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
