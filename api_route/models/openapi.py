import typing

from odoo import api, http, models


class OpenApi(models.Model):
    _name = "api_route.open_api"
    _description = (
        "OpenApi class containing methods to generate the openapi documentation"
    )

    @api.model
    def get_json(self: models.Model) -> typing.List[typing.Dict[str, str]]:
        router = http.root.get_db_router(http.request.db)
        rv = []
        for rule in router.iter_rules():
            if rule.endpoint.routing["type"] == "api":
                rv.append(
                    {
                        "details": rule.endpoint.routing,
                        "documentation": rule.endpoint.__doc__,
                        # "request": f"{rule.endpoint.func.__module__}::{rule.endpoint.func.__qualname__}",
                        "annotations": {
                            key: rule.endpoint.func.__annotations__[key].__dict__.get(
                                "__fields__"
                            )
                            if rule.endpoint.func.__annotations__[key].__dict__.get(
                                "__fields__", False
                            )
                            else rule.endpoint.func.__annotations__[key].__name__
                            for key in rule.endpoint.func.__annotations__
                        },
                    }
                )
        return rv
