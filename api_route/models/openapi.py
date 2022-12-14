# -*- coding: utf-8 -*-

# Copyright © Educacode.

import typing

from odoo import api, http, models
from pydantic.schema import schema


class OpenApi(models.Model):
    """
    Provide methods to create the OpenApi documentation
    of the type="api" routes
    """

    _name = "api_route.open_api"
    _description = (
        "OpenApi class containing methods to generate the openapi documentation"
    )

    @api.model
    def docstring_dict(self, doc: str) -> typing.Dict[str, str]:
        """
        Method to extract the @summary, @description, @tag from the docstring
        of any type="api" route
        """
        result = {}
        lines = doc.split("\n")
        for line in lines:
            if "@summary:" in line:
                result.update({"summary": line.replace("@summary:", "").strip()})
            if "@description:" in line:
                result.update(
                    {"description": line.replace("@description:", "").strip()}
                )
            if "@tag:" in line:
                result.update({"tag": line.replace("@tag:", "").strip()})

        return result

    @api.model
    def get_json(self: models.Model) -> typing.List[typing.Dict[str, str]]:
        """
        Method to return a valid OpenApi json
        """
        router = http.root.get_db_router(http.request.db)

        service_name = (
            self.env["ir.config_parameter"].sudo().get_param("api_route.service")
        )
        result = {
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
                            result["components"]["schemas"][obj] = current_schema[
                                "definitions"
                            ][obj]
                            if key == "return":
                                request_response = f"#/components/schemas/{obj}"
                            else:
                                request_body = f"#/components/schemas/{obj}"

                for path in rule.endpoint.routing.get("routes"):
                    for method in rule.endpoint.routing.get("methods"):
                        norm_method = method.lower()
                        path, path_parameters = self.extract_model(path)
                        if path not in result["paths"]:
                            result["paths"][path] = {}

                        docstring = (
                            rule.endpoint.func.__doc__
                            if rule.endpoint.func.__doc__
                            else "No Docstring"
                        )
                        docdict = self.docstring_dict(docstring)

                        result["paths"][path][norm_method] = {
                            "summary": docdict.get("summary"),
                            "description": docdict.get("description"),
                        }

                        if norm_method != "get":
                            result["paths"][path][norm_method].update(
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
                                }
                            )
                        if request_body:
                            result["paths"][path][norm_method].update(
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
                        if request_response:
                            result["paths"][path][norm_method].update(
                                {
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
                            )

                        if not "parameters" in result["paths"][path][norm_method]:
                            result["paths"][path][norm_method]["parameters"] = []
                        result["paths"][path][norm_method]["parameters"] += [
                            {
                                "in": "path",
                                "name": parameter.get("name"),
                                "schema": {"type": "integer"},
                                "required": True,
                                "description": f"Object id of model: {parameter.get('model')}",
                            }
                            for parameter in path_parameters
                        ]
                        if "tag" in docdict:
                            result["paths"][path][norm_method].update(
                                {"tags": [docdict["tag"]]}
                            )

        return result

    def extract_model(self, path, parameters=None):
        """Method to extract <model('module.model'):parameter> from the route path"""
        if parameters is None:
            parameters = []
        if "<" in path and ">" in path:
            to_extract = path[path.find("<") + 1 : path.find(">")]
            model = to_extract.split(":")[0]
            variable = to_extract.split(":")[1]
            parameters.append(
                {
                    "name": variable,
                    "model": model.replace("model(", "").replace(")", ""),
                }
            )
            path = path.replace(f"<{to_extract}>", f"{{{variable}}}")
            if "<" in path and ">" in path:
                return self.extract_model(path, parameters)
        return path, parameters
