# -*- coding: utf-8 -*-

# Copyright © Educacode.

from odoo import api, fields, models


class Cars(models.Model):
    _name = "example.todo"
    _description = "Todos example"

    name = fields.Char(string="Title")
    content = fields.Text(string="Content")
