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
    """
    Additionnal Dispatcher, any controller can use it by
    specifying type='api'
    """

    routing_type = "api"

    def __init__(self, request):
        super().__init__(request)
        self.jsonrequest = {}
        self.body = None

    def pre_dispatch(self, rule, args):
        """
        Add a check to the path args and raise 404 if the ressource
        doesn't exist.
        """
        for key in args:
            if (
                issubclass(type(args[key]), OdooBaseModel)
                and args[key].ids != args[key].exists().ids
            ):
                raise NotFound(f"The {key} with id {args[key].id} was not found")
        return super().pre_dispatch(rule, args)

    def switch(self, method, endpoint, args):
        """
        Simple Implementation of a switch case in python
        """
        return getattr(self, f"case_{method}", self.case_default)(endpoint, args)

    def case_get(self, endpoint, args):
        """
        Case Method GET
        """
        self.request.params = dict(self.request.get_http_params(), **args)
        return endpoint(**self.request.params)

    def case_post(self, endpoint, args):
        """
        Case Method POST
        """
        return self.json_body_method(endpoint, args)

    def case_patch(self, endpoint, args):
        """
        Case Method PATCH
        """
        return self.json_body_method(endpoint, args)

    def case_put(self, endpoint, args):
        """
        Case Method PUT
        """
        return self.json_body_method(endpoint, args)

    def case_delete(self, endpoint, args):
        """
        Case Method DELETE
        """
        self.request.params = dict(self.request.get_http_params(), **args)
        return endpoint(**self.request.params)

    def case_default(self, method, endpoint, args):
        """
        Case Default, Method Unknown
        """
        _logger.error(
            f"Dispatcher {endpoint} error unknown method: {method} with args: {args}",
        )
        raise InternalServerError("Unkown Method")

    def json_body_method(self, endpoint, args):
        """
        Helper function to process every request method
        which has a json body (POST, PATCH, PUT)
        """
        try:
            self.jsonrequest = self.request.get_json_data()
        except ValueError as err:
            raise UnprocessableEntity("Invalid Json") from err

        # Unmarshal provided JSON into the designated Object(BaseModel)
        body = self.unmarshal(endpoint)

        if issubclass(type(body), BaseModel):
            result = endpoint(body, **args)
        else:
            result = endpoint(**dict(self.jsonrequest, **args))
        return result

    @classmethod
    def is_compatible_with(cls, _):
        """
        Determine if the current request is compatible with this
        dispatcher.
        """
        return True

    def dispatch(self, endpoint, args):
        """
        Perform http-related actions such as deserializing the request
        body and query-string and checking cors/csrf while dispatching a
        request to a type='api' route.
        """
        if self.request.httprequest.method not in CSRF_FREE_METHODS:

            # Check CSRF token presence
            token = self.request.httprequest.headers.get("Csrf-Token")
            if endpoint.routing.get("csrf", True) and not token:
                raise Forbidden("Missing CSRF token")

            # Check CSRF is valid
            if token and not self.request.validate_csrf(token):
                raise BadRequest("Invalid CSRF token")

        result = self.switch(self.request.httprequest.method.lower(), endpoint, args)

        # if isinstance(result, Response):
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
        """
        Transform JSON body into a Pydantic (or Pydantic subclass)
        BaseModel instance
        """
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
            raise ApiUnprocessableEntity(str(err)) from err
