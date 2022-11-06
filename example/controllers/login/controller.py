# -*- coding: utf-8 -*-

# Copyright © Educacode.

from werkzeug.exceptions import Unauthorized

import odoo
from odoo import http

from .schema import LoginRequest, LoginResponse


class ApiLoginController(http.Controller):
    @http.route("/api/login", type="api", auth="none", methods=["POST"])
    def api_login(self, user: LoginRequest = None, **kw) -> LoginResponse:
        """
        @tag:         Auth
        @summary:     Login routes
        @description: Basic example for login route
        """
        http.request.update_env(user=odoo.SUPERUSER_ID)
        try:
            print(kw)
            http.request.session.authenticate(
                http.request.db,
                user.login,
                user.password,
            )
            return LoginResponse(success=True, csrf=http.request.csrf_token())

        except Exception as exc:
            raise Unauthorized("Login and/or Password invalid") from exc
