# -*- coding: utf-8 -*-

# Copyright © Educacode.
{
    "name": "api_route",
    "summary": """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",
    "description": """
        Long description of module's purpose
    """,
    "author": "Educacode",
    "website": "https://www.educacode.com",
    "category": "Website",
    "version": "1.0",
    "depends": ["base"],
    "external_dependancies": {"python": ["pydantic"]},
    "data": [
        "security/ir.model.access.csv",
        "views/config.xml",
        "views/menu.xml",
        "views/swagger.xml",
        "data/group.xml",
    ],
    "license": "LGPL-3",
}
