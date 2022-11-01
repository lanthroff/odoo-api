# -*- coding: utf-8 -*-

# Copyright © Educacode.

from odoo import http

from .schema import MyObject, MyObjectResponse


class ApiMyObjectController(http.Controller):
    @http.route("/api", type="api", auth="public", methods=["GET", "POST"])
    def api(self, data: MyObject = None, **kw) -> MyObjectResponse:
        """TEST DOCSTRING"""
        print(data.pretty())
        return MyObjectResponse(id=http.request.session.uid)
