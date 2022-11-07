# -*- coding: utf-8 -*-

# Copyright © Educacode.

import logging

from pydantic import BaseModel, ValidationError
from werkzeug.exceptions import (
    BadRequest,
    Forbidden,
    InternalServerError,
    MethodNotAllowed,
    NotFound,
    Unauthorized,
    UnprocessableEntity,
)

from odoo import http
from odoo.exceptions import AccessError
from odoo.http import CSRF_FREE_METHODS, Dispatcher, SessionExpiredException
from odoo.models import BaseModel as OdooBaseModel

from .exceptions import (
    ApiBadRequest,
    ApiForbidden,
    ApiInternalServerError,
    ApiMethodNotAllowed,
    ApiNotFound,
    ApiUnauthorized,
    ApiUnprocessableEntity,
)

_logger = logging.getLogger(__name__)


class ApiDispatcher(Dispatcher):
    routing_type = "api"

    def __init__(self, request):
        super().__init__(request)
        self.jsonrequest = {}
        self.body = None

    def pre_dispatch(self, rule, args):
        """
        Add a check to the path args and raise 404 if the ressource
        doesn't exist
        """
        # Maybe choose this version with no error raise instead
        # args = {
        #     key: args[key].exists()
        #     if issubclass(type(args[key]), OdooBaseModel)
        #     else args[key]
        #     for key in args
        # }
        for key in args:
            if (
                issubclass(type(args[key]), OdooBaseModel)
                and args[key].ids != args[key].exists().ids
            ):
                raise NotFound(f"The {key} with id {args[key].id} was not found")
        return super().pre_dispatch(rule, args)

    # TODO DRY
    def switch(self, method, endpoint, args):
        return getattr(self, f"case_{method}", self.case_default)(
            method, endpoint, args
        )

    def case_get(self, method, endpoint, args):
        self.request.params = dict(self.request.get_http_params(), **args)
        result = endpoint(**self.request.params)
        return result

    def case_post(self, method, endpoint, args):
        try:
            self.jsonrequest = self.request.get_json_data()
        except ValueError as _:
            raise UnprocessableEntity("Invalid Json")

        # Unmarshal provided JSON into the designated Object(BaseModel)
        body = self.unmarshal(endpoint)

        if issubclass(type(body), BaseModel):
            result = endpoint(body, **args)
        else:
            result = endpoint(**dict(self.jsonrequest, **args))
        return result

    def case_patch(self, method, endpoint, args):
        try:
            self.jsonrequest = self.request.get_json_data()
        except ValueError as _:
            raise UnprocessableEntity("Invalid Json")

        # Unmarshal provided JSON into the designated Object(BaseModel)
        body = self.unmarshal(endpoint)
        if issubclass(type(body), BaseModel):
            result = endpoint(body, **args)
        else:
            result = endpoint(**dict(self.jsonrequest, **args))
        return result

    def case_put(self, method, endpoint, args):
        try:
            self.jsonrequest = self.request.get_json_data()
        except ValueError as _:
            raise UnprocessableEntity("Invalid Json")

        # Unmarshal provided JSON into the designated Object(BaseModel)
        body = self.unmarshal(endpoint)
        if issubclass(type(body), BaseModel):
            result = endpoint(body, **args)
        else:
            result = endpoint(**dict(self.jsonrequest, **args))
        return result

    def case_delete(self, method, endpoint, args):
        self.request.params = dict(self.request.get_http_params(), **args)
        result = endpoint(**self.request.params)
        return result

    def case_default(self, method, endpoint, args):
        _logger.error(f"Dispatcher error unknown method: {method}")
        raise InternalServerError("Unkown Method")

    @classmethod
    def is_compatible_with(cls, request):
        return True

    def dispatch(self, endpoint, args):
        # import inspect

        # print(args)
        # print(inspect.signature(endpoint.func))

        if self.request.httprequest.method not in CSRF_FREE_METHODS:

            # Check CSRF token presence
            token = self.request.httprequest.headers.get("Csrf-Token")
            if endpoint.routing.get("csrf", True) and not token:
                raise Forbidden("Missing CSRF token")

            # Check CSRF is valid
            if token and not self.request.validate_csrf(token):
                raise BadRequest("Invalid CSRF token")

        result = self.switch(self.request.httprequest.method.lower(), endpoint, args)

        # if self.request.httprequest.method not in CSRF_FREE_METHODS:
        #     # BEGIN REFACTOR SECTION
        #     # Check JSON is valid
        #     try:
        #         self.jsonrequest = self.request.get_json_data()
        #     except ValueError as _:
        #         raise UnprocessableEntity("Invalid Json")

        #     # Unmarshal provided JSON into the designated Object(BaseModel)
        #     self.body = self.unmarshal(endpoint)

        # self.request.params = dict(self.jsonrequest, **args)

        # ctx = self.request.params.pop("context", None)
        # if ctx is not None and self.request.db:
        #     self.request.update_env(context=ctx)

        # if self.request.db:
        #     result = self._dispatch(endpoint)
        # else:
        #     result = endpoint(**self.request.params)

        # if isinstance(result, Response):
        #     print("NEVER TRUE")
        #     result.flatten()

        if issubclass(type(result), BaseModel):
            result = result.dict()

        return self.request.make_json_response(result)

    def handle_error(self, exc):
        """
        Handle any error that occured during dispatch
        """
        if isinstance(exc, BadRequest):
            response = ApiBadRequest(exc.description)
        elif isinstance(exc, SessionExpiredException):
            session = self.request.session
            session.logout(keep_db=True)
            response = ApiUnauthorized("Session Expired")
        elif isinstance(exc, AccessError):
            response = InternalServerError(exc.args[0])
        elif isinstance(exc, Unauthorized):
            response = ApiUnauthorized(exc.description)
        elif isinstance(exc, Forbidden):
            response = ApiForbidden(exc.description)
        elif isinstance(exc, MethodNotAllowed):
            response = ApiMethodNotAllowed(exc.description)
        elif isinstance(exc, UnprocessableEntity):
            response = ApiUnprocessableEntity(exc.description)
        elif isinstance(exc, NotFound):
            response = ApiNotFound(exc.description)
        elif isinstance(exc, InternalServerError):
            response = ApiInternalServerError()
        else:
            response = ApiInternalServerError(str(exc))

        return response.get_response()

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
        except ValidationError as err:
            _logger.error(err)
            raise ApiUnprocessableEntity(str(err))

    # def _dispatch(self, endpoint):
    #     if self.body:
    #         result = endpoint(self.body)
    #     else:
    #         result = endpoint(**http.request.params)
    #     if isinstance(result, Response):
    #         result.flatten()
    #     return result
