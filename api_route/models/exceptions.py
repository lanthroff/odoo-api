# -*- coding: utf-8 -*-

# Copyright © Educacode.

from email.policy import HTTP

from werkzeug.exceptions import (
    BadRequest,
    Forbidden,
    InternalServerError,
    MethodNotAllowed,
    Unauthorized,
    UnprocessableEntity,
)


class ApiBadRequest(BadRequest):
    def get_body(self, environ=None):
        return self.description


class ApiForbidden(Forbidden):
    def get_body(self, environ=None):
        return self.description


class ApiInternalServerError(InternalServerError):
    def get_body(self, environ=None):
        return self.description


class ApiMethodNotAllowed(MethodNotAllowed):
    def get_body(self, environ=None):
        return self.description


class ApiUnauthorized(Unauthorized):
    def get_body(self, environ=None):
        return self.description


class ApiUnprocessableEntity(UnprocessableEntity):
    def get_body(self, environ=None):
        return self.description


# TODO
# RECONCILIER AVEC AXIOS
# PASSER EN HISTORYROUTER
