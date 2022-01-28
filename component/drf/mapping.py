# -*- coding: utf-8 -*-
from component.utils.exceptions import (AuthenticationError, NotAuthenticatedError,
                                        PermissionDeniedError, MethodNotAllowedError,
                                        NotAcceptableError, UnsupportedMediaTypeError,
                                        ThrottledError, ParamValidationError, ResourceNotFound)

# drf exception to blueapps exception
exception_mapping = {
    "ValidationError": ParamValidationError,
    "AuthenticationFailed": AuthenticationError,
    "NotAuthenticated": NotAuthenticatedError,
    "PermissionDenied": PermissionDeniedError,
    "NotFound": ResourceNotFound,
    "MethodNotAllowed": MethodNotAllowedError,
    "NotAcceptable": NotAcceptableError,
    "UnsupportedMediaType": UnsupportedMediaTypeError,
    "Throttled": ThrottledError
}
