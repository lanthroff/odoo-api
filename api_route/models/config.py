# -*- coding: utf-8 -*-

# Copyright © Educacode.

from odoo import fields, models


class ReactConfig(models.TransientModel):
    _inherit = "res.config.settings"

    website = fields.Char(string="Website uri")

    def get_values(self):
        res = super().get_values()
        get_param = self.env["ir.config_parameter"].sudo().get_param
        res.update(
            website=get_param("api_route.website"),
        )
        return res

    def set_values(self):
        super().set_values()
        set_param = self.env["ir.config_parameter"].sudo().set_param
        set_param("api_route.website", self.website)
