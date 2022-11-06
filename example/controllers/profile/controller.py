# -*- coding: utf-8 -*-

# Copyright © Educacode.

from odoo import http

from .schema import ProfileResponse


class ApiProfileController(http.Controller):
    @http.route("/profile", type="api", auth="user", methods=["GET", "POST"])
    def profile(self, **kw) -> ProfileResponse:
        todo_ids = http.request.env["example.todo"].search(
            [("create_uid", "=", http.request.session.uid)]
        )
        return {
            "user": {
                "id": http.request.env.user.id,
                "name": http.request.env.user.name,
            },
        }
