# -*- coding: utf-8 -*-

# Copyright © Educacode.

from odoo import api, fields, models


class Cars(models.Model):
    _name = "example.cars"
    _description = "example.cars"

    name = fields.Char(compute="_compute_name", store=True)
    owner = fields.Many2one("res.users", string="Owner")
    brand = fields.Char(string="Brand", default="")
    model = fields.Char(string="Model", default="")
    number = fields.Char(string="Plate number", default="")

    @api.depends("brand", "model", "number")
    def _compute_name(self):
        for record in self:
            record.name = f"{record.brand} {record.model} {record.number}"
