# -*- coding: utf-8 -*-

# Copyright © Educacode.


from odoo import http
from odoo.addons.web.controllers.utils import ensure_db
from werkzeug.exceptions import Unauthorized


class ApiRouteController(http.Controller):
    @http.route("/documentation", type="http", auth="user", methods=["GET"])
    def documentation(self):
        if not http.request.env.user.has_group(
            "api_route.group_api_route_documentation"
        ):
            return Unauthorized("You don't have permission to see the documentation")

        return http.request.render("api_route.swagger")

    @http.route("/docs", type="api", auth="user", methods=["GET"])
    def docs(self):
        if not http.request.env.user.has_group(
            "api_route.group_api_route_documentation"
        ):
            return Unauthorized("You don't have permission to see the documentation")

        return http.request.env["api_route.open_api"].get_json(
            http.request.httprequest.url.replace("/docs", "")
        )
