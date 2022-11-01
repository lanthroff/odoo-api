# -*- coding: utf-8 -*-

# Copyright © Educacode.

import odoo
from odoo import http
from odoo.addons.web.controllers.utils import ensure_db
from werkzeug.exceptions import Unauthorized

from .schema import LoginRequest, LoginResponse


class ApiLoginController(http.Controller):
    @http.route("/api/login", type="api", auth="none", methods=["POST"])
    def api_login(self, user: LoginRequest) -> LoginResponse:
        """
        @tag:         Auth
        @summary:     Login routes
        @description: Basic example for login route
        """
        ensure_db()

        http.request.update_env(user=odoo.SUPERUSER_ID)
        try:
            uid = http.request.session.authenticate(
                http.request.db,
                user.login,
                user.password,
            )
            return LoginResponse(success=True, csrf=http.request.csrf_token())

        except Exception as e:
            raise Unauthorized("Login and/or Password invalid")
