# -*- coding: utf-8 -*-

# Copyright © Educacode.

from odoo import fields, models


class ApiRouteConfig(models.TransientModel):
    _inherit = "res.config.settings"

    service = fields.Char(string="Service name")

    def get_values(self):
        res = super().get_values()
        get_param = self.env["ir.config_parameter"].sudo().get_param
        res.update(
            service=get_param("api_route.service"),
        )
        return res

    def set_values(self):
        super().set_values()
        set_param = self.env["ir.config_parameter"].sudo().set_param
        set_param("api_route.service", self.service)

    def go_documentation(self):
        return {
            "type": "ir.actions.act_url",
            "url": "/documentation",
            "target": "self",
        }
