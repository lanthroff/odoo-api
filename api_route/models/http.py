# -*- coding: utf-8 -*-

# Copyright © Educacode.

import logging

from odoo import http
from odoo.exceptions import AccessError
from odoo.http import CSRF_FREE_METHODS, Dispatcher, Response, SessionExpiredException
from pydantic import BaseModel, ValidationError
from werkzeug.exceptions import (
    BadRequest,
    Forbidden,
    InternalServerError,
    MethodNotAllowed,
    Unauthorized,
    UnprocessableEntity,
)

from .exceptions import (
    ApiBadRequest,
    ApiForbidden,
    ApiInternalServerError,
    ApiMethodNotAllowed,
    ApiUnauthorized,
    ApiUnprocessableEntity,
)

_logger = logging.getLogger(__name__)


class ApiDispatcher(Dispatcher):
    """
    Error Codes:
        - 400 BadRequest: Invalid CSRF token
        - 401 Unauthorized: User not logged in
        - 403 Forbidden: Missing CSRF token
        - 405 Method Not Allowed
        - 422 UnprocessableEntity: Json invalid
        - 500 Internal server error
    """

    routing_type = "api"

    def __init__(self, request):
        super().__init__(request)
        self.jsonrequest = {}
        self.body = None

    @classmethod
    def is_compatible_with(cls, request):
        return True

    def dispatch(self, endpoint, args):
        if self.request.httprequest.method not in CSRF_FREE_METHODS:

            # Check CSRF token presence
            token = self.request.httprequest.headers.get("Csrf-Token")
            if endpoint.routing.get("csrf", True) and not token:
                return ApiForbidden("Missing CSRF token").get_response()

            # Check CSRF is valid
            if token and not self.request.validate_csrf(token):
                return ApiBadRequest().get_response()

            # Check JSON is valid
            try:
                self.jsonrequest = self.request.get_json_data()
            except ValueError as exc:
                return ApiUnprocessableEntity("Invalid Json").get_response()

            # Unmarshal provided JSON into the designated Object(BaseModel)
            self.body = self.unmarshal(endpoint)

        self.request.params = dict(self.jsonrequest, **args)

        ctx = self.request.params.pop("context", None)
        if ctx is not None and self.request.db:
            self.request.update_env(context=ctx)

        if self.request.db:
            # result = self.request.registry["ir.http"]._dispatch(endpoint)
            result = self._dispatch(endpoint)
        else:
            result = endpoint(**self.request.params)

        # TODO MARSHAL THE RESPONSE OBJECT -> JSON
        return self.request.make_json_response(result)

    def handle_error(self, exc):
        if isinstance(exc, BadRequest):
            return ApiBadRequest(exc.description).get_response()
        elif isinstance(exc, SessionExpiredException):
            session = self.request.session
            session.logout(keep_db=True)
            return ApiUnauthorized("Session Expired").get_response()
        elif isinstance(exc, AccessError):
            return InternalServerError(exc.args[0])
        elif isinstance(exc, Unauthorized):
            return ApiUnauthorized(exc.description).get_response()
        elif isinstance(exc, Forbidden):
            return ApiForbidden(exc.description).get_response()
        elif isinstance(exc, MethodNotAllowed):
            return ApiMethodNotAllowed(exc.description).get_response()
        elif isinstance(exc, UnprocessableEntity):
            return ApiUnprocessableEntity(exc.description).get_response()
        elif isinstance(exc, InternalServerError):
            return ApiInternalServerError().get_response()
        else:
            return ApiInternalServerError(str(exc)).get_response()

    def unmarshal(self, endpoint):
        annotations = list(
            filter(
                lambda key: issubclass(
                    endpoint.func.__annotations__.get(key), BaseModel
                )
                and key != "return",
                endpoint.func.__annotations__,
            )
        )
        argument = annotations[0] if annotations else None

        try:
            return (
                endpoint.func.__annotations__.get(argument)(**self.jsonrequest)
                if argument
                else None
            )
        except ValidationError as e:
            _logger.error(e)
            raise ApiUnprocessableEntity(str(e))

    def _dispatch(self, endpoint):
        if self.body:
            result = endpoint(self.body)
        else:
            result = endpoint(**http.request.params)
        if isinstance(result, Response):
            result.flatten()
        return result
