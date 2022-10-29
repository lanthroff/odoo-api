# -*- coding: utf-8 -*-

# Copyright © Educacode.

import json

import odoo
from odoo import http
from odoo.addons.web.controllers.utils import ensure_db
from werkzeug.exceptions import Unauthorized


class ApiRouteController(http.Controller):
    @http.route("/ping", type="api", auth="none", methods=["GET"])
    def ping(self, **kw):
        return {
            "csrf": http.request.csrf_token(),
            "user": False
            if not http.request.session.uid
            else http.request.session.uid
            != http.request.env.ref("base.public_user").id,
        }

    @http.route("/api/login", type="api", auth="none", methods=["POST"])
    def api_login(self, redirect=None, **kw):
        ensure_db()

        http.request.update_env(user=odoo.SUPERUSER_ID)
        try:
            uid = http.request.session.authenticate(
                http.request.db,
                kw.get("login", ""),
                kw.get("password", ""),
            )
            return {"success": True, "csrf": http.request.csrf_token()}

        except Exception as e:
            raise Unauthorized()

    @http.route("/documentation", type="http", auth="user", methods=["GET"])
    def documentation(self):
        if not http.request.env.user.has_group(
            "api_route.group_api_route_documentation"
        ):
            return Unauthorized("You don't have permission to see the documentation")

        return http.request.render("api_route.swagger")

    @http.route("/docs", type="http", auth="user", methods=["GET"])
    def docs(self, **kw):
        if not http.request.env.user.has_group(
            "api_route.group_api_route_documentation"
        ):
            return Unauthorized("You don't have permission to see the documentation")

        return http.request.env["api_route.open_api"].get_json()
