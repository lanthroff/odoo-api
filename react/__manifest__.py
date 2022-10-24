# -*- coding: utf-8 -*-

# Copyright © Educacode.
{
    "name": "react",
    "summary": """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",
    "description": """
        Long description of module's purpose
    """,
    "author": "Educacode",
    "website": "https://www.educacode.com",
    "category": "Website",
    "version": "0.1",
    "depends": ["base"],
    "data": [
        "security/ir.model.access.csv",
        "views/config.xml",
        "views/menu.xml",
    ],
    "demo": [
        "demo/demo.xml",
    ],
    "license": "LGPL-3",
}
