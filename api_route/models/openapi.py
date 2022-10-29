# -*- coding: utf-8 -*-

# Copyright © Educacode.

import json
import typing

import odoo
from odoo import api, http, models
from pydantic import BaseModel, Extra
from pydantic.schema import schema


class ApiModel(BaseModel):
    def __str__(self):
        return f"{self.__class__.__name__}({', '.join([ f'{key}={self.__dict__.get(key)}' for key in self.__dict__])})"

    def pretty(self, h="*", v="|"):
        """
        Do not disturb
        """
        h = h[0] if len(h) > 1 else h
        v = v[0] if len(v) > 1 else v
        width = max(
            [len(self.__class__.__name__) + 12]
            + [len(f"{key}: {getattr(self, key)}") + 4 for key in self.__dict__]
        )
        if (width - len(self.__class__.__name__)) % 2:
            width += 1

        header = (
            f"{h * (((width - len(self.__class__.__name__)) // 2) - 1 ) } {self.__class__.__name__} {h * (((width - len(self.__class__.__name__)) // 2) - 1 ) }"
            + "\n"
            + f"{v}{' ' * (width - 2)}{v}"
            + "\n"
        )
        footer = f"{v}{' ' * (width - 2)}{v}" + "\n" + h * width + "\n"
        result = "\n"
        result += header
        for key in self.__dict__:
            data = f"{key}: {getattr(self, key)}"
            result += f"{v} {data}{' ' * (width - len(data) - 3)}{v}" + "\n"
        result += footer
        return result

    class Config:
        extra = Extra.forbid


class OpenApi(models.Model):
    _name = "api_route.open_api"
    _description = (
        "OpenApi class containing methods to generate the openapi documentation"
    )

    @api.model
    def get_json(self: models.Model) -> typing.List[typing.Dict[str, str]]:
        router = http.root.get_db_router(http.request.db)

        Params = self.env["ir.config_parameter"].sudo()

        current_host = Params.get_param("web.base.url")
        # current_host = (
        #     f"{current_host}:{odoo.tools.config.options.get('http_port')}"
        #     if "http://localhost" in current_host
        #     else current_host
        # )

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
                            ref_prefix="#components/schema/",
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
                            if not path in rv["paths"]:
                                rv["paths"][path] = {}

                            rv["paths"][path][norm_method] = {
                                "summary": rule.endpoint.func.__doc__,
                                "description": rule.endpoint.func.__doc__,
                                "responses": {
                                    "200": {
                                        "description": "Successful operation",
                                        "content": {
                                            "application/json": {
                                                "schema": {"$ref": request_response}
                                            },
                                        },
                                    },
                                    "400": {"description": "Invalid ID supplied"},
                                    "404": {"description": "Pet not found"},
                                    "405": {"description": "Validation exception"},
                                },
                            }
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

        return json.dumps(rv)
