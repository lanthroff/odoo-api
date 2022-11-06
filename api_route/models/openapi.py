# -*- coding: utf-8 -*-

# Copyright © Educacode.

import typing

from odoo import api, http, models
from pydantic.schema import schema


class OpenApi(models.Model):
    _name = "api_route.open_api"
    _description = (
        "OpenApi class containing methods to generate the openapi documentation"
    )

    @api.model
    def docstring_dict(self, doc: str) -> typing.Dict[str, str]:
        rv = {}
        lines = doc.split("\n")
        for line in lines:
            if "@summary:" in line:
                rv.update({"summary": line.replace("@summary:", "").strip()})
            if "@description:" in line:
                rv.update({"description": line.replace("@description:", "").strip()})
            if "@tag:" in line:
                rv.update({"tag": line.replace("@tag:", "").strip()})

        return rv

    @api.model
    def get_json(
        self: models.Model, current_host: str
    ) -> typing.List[typing.Dict[str, str]]:
        router = http.root.get_db_router(http.request.db)

        Params = self.env["ir.config_parameter"].sudo()

        service_name = Params.get_param("api_route.service")
        rv = {
            "openapi": "3.0.3",
            "info": {
                "title": service_name,
                "description": "This is the documentation for your Odoo api_route",
                "termsOfService": "http://swagger.io/terms/",
                "contact": {"email": "clement.marlier@ie-mob.com"},
                "license": {
                    "name": "LGPL-3",
                    "url": "https://www.gnu.org/licenses/lgpl-3.0.html",
                },
                "version": "1.0.0",
            },
            "externalDocs": {
                "description": "Find out more about Swagger",
                "url": "http://swagger.io",
            },
            "servers": [{"url": current_host}],
            "paths": {},
            "components": {
                "schemas": {},
            },
        }

        router = http.root.get_db_router(http.request.db)
        csrf_token = http.request.csrf_token()

        for rule in router.iter_rules():
            if rule.endpoint.routing["type"] == "api":

                request_body = None
                request_response = None

                # Iterate over all the annotations in the route definition
                for key in rule.endpoint.func.__annotations__:
                    # If the annotation is of type object then we get the details
                    if hasattr(rule.endpoint.func.__annotations__[key], "__fields__"):

                        # Convert the schema to openapi dict
                        current_schema = schema(
                            [rule.endpoint.func.__annotations__[key]],
                            ref_prefix="#/components/schemas/",
                        )
                        for obj in current_schema["definitions"]:
                            rv["components"]["schemas"][obj] = current_schema[
                                "definitions"
                            ][obj]
                            if key == "return":
                                request_response = f"#/components/schemas/{obj}"
                            else:
                                request_body = f"#/components/schemas/{obj}"

                for path in rule.endpoint.routing.get("routes"):
                    for method in rule.endpoint.routing.get("methods"):
                        norm_method = method.lower()
                        if request_response and (request_body or norm_method == "get"):
                            if path not in rv["paths"]:
                                rv["paths"][path] = {}

                            docstring = (
                                rule.endpoint.func.__doc__
                                if rule.endpoint.func.__doc__
                                else "No Docstring"
                            )
                            docdict = self.docstring_dict(docstring)

                            rv["paths"][path][norm_method] = {
                                "summary": docdict.get("summary"),
                                "description": docdict.get("description"),
                                "responses": {
                                    "200": {
                                        "description": "Successful operation",
                                        "content": {
                                            "application/json": {
                                                "schema": {"$ref": request_response}
                                            },
                                        },
                                    },
                                },
                            }
                            if "tag" in docdict:
                                rv["paths"][path][norm_method].update(
                                    {"tags": [docdict["tag"]]}
                                )
                            if norm_method != "get":
                                rv["paths"][path][norm_method].update(
                                    {
                                        "parameters": [
                                            {
                                                "in": "header",
                                                "name": "Csrf-Token",
                                                "schema": {
                                                    "type": "string",
                                                    "default": csrf_token,
                                                },
                                            },
                                        ],
                                        "requestBody": {
                                            "description": "",
                                            "content": {
                                                "application/json": {
                                                    "schema": {"$ref": request_body}
                                                },
                                            },
                                            "required": True,
                                        },
                                    }
                                )

        return rv
