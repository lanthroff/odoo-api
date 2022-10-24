import logging

from odoo import http
from odoo.http import CSRF_FREE_METHODS, Dispatcher, SessionExpiredException
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

    @classmethod
    def is_compatible_with(cls, request):
        return request.httprequest.mimetype == "application/json"

    def dispatch(self, endpoint, args):
        # Check json validity if not GET type
        self.jsonrequest = {}
        if self.request.httprequest.method != "GET":
            try:
                self.jsonrequest = self.request.get_json_data()
            except ValueError as exc:
                return ApiUnprocessableEntity("Invalid Json").get_response()

        # Check Csrf token presence if needed
        token = self.jsonrequest.pop("csrf_token", None)
        if (
            self.request.httprequest.method not in CSRF_FREE_METHODS
            and endpoint.routing.get("csrf", True)
            and not token
        ):
            return ApiForbidden("Missing CSRF token").get_response()

        # Check csrf validity if needed
        if token and not self.request.validate_csrf(token):
            return ApiBadRequest().get_response()

        # TODO choose if we keep the flexibility to receive args in url
        # union_params = self.request.get_http_params()
        # for p in self.jsonrequest:
        #     union_params[p] = self.jsonrequest.get(p)
        # self.request.params = dict(union_params, **args)

        self.request.params = dict(self.jsonrequest, **args)

        ctx = self.request.params.pop("context", None)
        if ctx is not None and self.request.db:
            self.request.update_env(context=ctx)

        if self.request.db:
            result = self.request.registry["ir.http"]._dispatch(endpoint)
        else:
            result = endpoint(**self.request.params)
        return self.request.make_json_response(result)

    def handle_error(self, exc):
        if isinstance(exc, BadRequest):
            return ApiBadRequest(exc.args[0]).get_response()
        elif isinstance(exc, SessionExpiredException):
            session = self.request.session
            session.logout(keep_db=True)
            return ApiUnauthorized("Session Expired").get_response()
        elif isinstance(exc, Unauthorized):
            return ApiUnauthorized("Login/Password invalid").get_response()
        elif isinstance(exc, Forbidden):
            return ApiForbidden(exc.args[0]).get_response()
        elif isinstance(exc, MethodNotAllowed):
            return ApiMethodNotAllowed(exc.args[0]).get_response()
        elif isinstance(exc, UnprocessableEntity):
            return ApiUnprocessableEntity(exc.args[0]).get_response()
        elif isinstance(exc, InternalServerError):
            return ApiInternalServerError().get_response()
        else:
            return ApiInternalServerError("Unknown Error").get_response()
