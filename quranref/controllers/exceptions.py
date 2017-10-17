"""
Exceptions / Errors raised by the API
=====================================

List of API error classes.
"""

import json
from pyramid.httpexceptions import (
    HTTPBadRequest, HTTPClientError, HTTPException, HTTPForbidden,
    HTTPInsufficientStorage, HTTPMethodNotAllowed, HTTPNotAcceptable,
    HTTPTooManyRequests, HTTPNotFound, HTTPUnauthorized, HTTPBadRequest
)


def stripstr(s):
    new_s = s.strip().replace("\n", " ")
    while -1 != new_s.find('  '):
        new_s = new_s.replace("  ", " ")

    return new_s


class ErrorResponse(object):
    """
    Class representing a response object parsed from a :class:`webtest.app.AppError` instance.
    Basically parses the string representation of the :class:`webtest.app.AppError.exception` object.
    """

    def __init__(self, app_error):
        "Initialize ErrorResponse object from given AppError instance"
        error_message = str(app_error.exception)
        #TODO: Find a way to fetch the actual exception detail
        # Bad response: 429 Too Many Requests (not 200 OK or 3xx redirect for http://localhost/api/v1/user/verify_account)
        # {"error_message": "Too many requests were made to the resource and further requests are not allowed anymore", "error_code": 4290}
        self.status = ''
        self.status_int = None
        self.json_body = None
        self.body = None

        lines = error_message.split('\n')
        if lines:
            status_line = lines[0]
            self.status = status_line.strip('Bad response: ').split('(')[0].strip()
            self.status_int = int(self.status.split(' ')[0])

            if len(lines) > 1:
                remaining_content = '\n'.join(lines[1:])
                self.body = remaining_content
                try:
                    self.json_body = json.loads(remaining_content)
                except json.JSONDecodeError:
                    self.json_body = None

    def raises(self, api_error_class):
        "Verifies if the current error response's contents match those of given API error class"

        return bool(self.json_body and 'error_code' in self.json_body and
                    self.json_body['error_code'] == api_error_class.error_code)


class APIError(HTTPException):
    """
    Base class for all API errors. Adds the extra parameters of error_code and error_message.

    :param error_code:
        The API specific error code for the problem. The convention used is that the error code always begins with
        the HTTP error code and then adds it's own error digits after that. For example a generic forbidden error code
        might be 4030 where 403 is the HTTP response code for FORBIDDEN and the next 0 denotes our own error category.

    :param error_message:
        The error message detailing the error.
    """

    error_code = 1000
    error_message = stripstr(__doc__)
    custom_message = None

    def __init__(self, detail=None, **kw):
        if not detail:
            detail = self.error_message

        self.custom_message = detail

        headers = [
            ('Access-Control-Allow-Origin', '*'), ('Content-Type', 'application/json; charset=utf-8'),
            ("Access-Control-Allow-Headers", "Content-Type, Access-Control-Allow-Headers, Authorization, X-Requested-With"),
            ("Access-Control-Allow-Methods", "GET,POST,PUT,DELETE,OPTIONS,HEAD")
        ]

        if 'headers' in kw:
            headers.update(kw['headers'])

        kw['headers'] = headers

        super().__init__(detail=detail, **kw)

    def prepare(self, environ):
        self.content_type = "application/json"
        self.charset = 'utf-8'

        page = json.dumps(dict(error_code=self.error_code, error_message=self.custom_message)).encode(self.charset)

        self.app_iter = [page]
        self.body = page


class APIForbidden(APIError, HTTPForbidden):
    "This resource cannot be accessed without providing a valid auth token in the request"

    error_code = 4030
    error_message = stripstr(__doc__)


class APIInsufficientPermissions(APIForbidden):
    "User does not have enough permissions to access the resource"

    error_code = 4031
    error_message = stripstr(__doc__)


class APIMethodNotAllowed(APIError, HTTPMethodNotAllowed):
    "HTTP method not supported by this API endpoint"

    error_code = 4050
    error_message = stripstr(__doc__)


class APIBadRequest(APIError, HTTPBadRequest):
    "Request could not be understood by the API"

    error_code = 4000
    error_message = stripstr(__doc__)


class APINoAuthToken(APIForbidden):
    "No authentication token found in the request"

    error_code = 4031
    error_message = stripstr(__doc__)


class APIInvalidToken(APIForbidden):
    """
    The provided auth token is not valid. Returned in cases where the token's signature is invalid, it has invalid
    or incomplete claims or the token has expired.
    """

    error_code = 4032
    error_message = stripstr(__doc__)


class APIBadToken(APIBadRequest):
    """
    The auth token provided is not in the correct format. The correct method of specifying the auth token is to send
    it in the request's Authorization header with the bearer keyword. For example:

    Authorization: BEARER the_actual_auth_token
    """

    error_code = 4001
    error_message = stripstr(__doc__)


class APITooManyRequests(APIError, HTTPTooManyRequests):
    "Too many requests were made to the resource and further requests are not allowed anymore"

    error_code = 4290
    error_message = stripstr(__doc__)
