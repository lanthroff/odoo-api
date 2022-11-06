# -*- coding: utf-8 -*-

# Copyright © Educacode.

from werkzeug.exceptions import (
    BadRequest,
    Forbidden,
    InternalServerError,
    MethodNotAllowed,
    NotFound,
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


class ApiNotFound(NotFound):
    def get_body(self, environ=None):
        return self.description
