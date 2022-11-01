# -*- coding: utf-8 -*-

# Copyright © Educacode.

from odoo import http

from .schema import PingResponse


class ApiPingController(http.Controller):
    @http.route("/ping", type="api", auth="none", methods=["GET"])
    def api_ping(self) -> PingResponse:
        """
        @tag:         Auth
        @summary:     Csrf token
        @description: Simple GET route to provide a Csrf token

        """

        return PingResponse(
            csrf=http.request.csrf_token(),
            user=False
            if not http.request.session.uid
            else http.request.session.uid
            != http.request.env.ref("base.public_user").id,
        )
