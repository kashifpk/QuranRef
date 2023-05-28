"""
API Base Functionality
=======================

This module contains functionality common to all classes that implement API endpoints
"""

import logging
import json
import collections
from pyramid.httpexceptions import HTTPNoContent
from .exceptions import APIForbidden, APIMethodNotAllowed, APINoAuthToken, APIBadRequest

log = logging.getLogger(__name__)


class RequestParameters(collections.abc.MutableMapping):
    """
    Class that collects parameters from JSON request body. Also allows methods to verify that all
    required parameters are present
    """

    def __init__(self, request):
        """
        Parse the request object and populate request parameters
        """
        try:
            self.params = request.json_body
        except (json.decoder.JSONDecodeError, AssertionError):
            self.params = {}

    def __getitem__(self, key):
        return self.params[key]

    def __setitem__(self, key, value):
        self.params[key] = value

    def __delitem__(self, key):
        del self.params[key]

    def __iter__(self):
        return iter(self.params)

    def __len__(self):
        return len(self.params)

    def __repr__(self):
        return str(self.params)

    def assert_all(self, keys, exp_to_raise=AssertionError):
        "Assert that all given keys are present in the request parameters collection"

        for key in keys:
            if key not in self.params:
                raise exp_to_raise

        return True

    def assert_any(self, keys, exp_to_raise=AssertionError):
        "Assert that any of the given keys is present in the request parameters collection"

        for key in keys:
            if key in self.params:
                return True

        raise exp_to_raise


class APILogRecord(object):
    "Custom class containing a log record from the API"

    def __init__(self, request, event_type, message, user_id=None, extra_info=None):
        # Request gets us user_agent, ip and user_id if authenticated (from JWT)
        self.request = request
        self.event_type = event_type
        self.message = message
        self.extra_info = extra_info
        self.user_id = user_id
        if not user_id and hasattr(request, 'auth_token'):
            self.user_id = request.auth_token['aud']

    def __str__(self):
        return "APILog - [{0.user_id} - {0.event_type}] {0.message}".format(self)


class APIBase(object):
    """
    Better Base class for all the API implementation classes. Handles stuff like:

    * Allowing CORS requests
    * Returning proper response to HTTP OPTIONS method. This is requested by all modern browsers when making XHR calls.

    :param _HTTP_ALLOWED_METHODS: (List) specified the HTTP methods the current class implementing an API endpoint supports
    """

    _ENDPOINTS = {
        'GET': [
            # (endpoint, method_to_call),
        ]
    }

    _log = log

    def __init__(self, request):
        self.request = request
        self.endpoint_info = {}
        self.request_params = None

    def _cors_headers(self):
        return {
            'Access-Control-Allow-Origin': '*', 'Content-Type': 'application/json; charset=utf-8',
            "Access-Control-Allow-Headers": "Content-Type, Access-Control-Allow-Headers, Authorization, X-Requested-With",
            "Access-Control-Allow-Methods": ",".join(self._ENDPOINTS.keys())
        }

    def _match_endpoint(self, ep):

        request_ep = self.request.matchdict['endpoint']
        endpoint_to_match = ep[0]

        if 0 == len(request_ep) and '' == endpoint_to_match:
            self.endpoint_info = {}
            return True

        if endpoint_to_match != '':
            ep_parts = endpoint_to_match.split('/')

            if len(request_ep) == len(ep_parts):
                # Both have same number of url slash fragments, lets see if the non {} fragments match

                for i in range(len(ep_parts)):

                    if ep_parts[i].startswith('{') and ep_parts[i].endswith('}'):
                        k = ep_parts[i][1:-1]
                        self.endpoint_info[k] = request_ep[i]

                    elif ep_parts[i] != request_ep[i]:
                        self.endpoint_info = {}
                        return False

                return True

        return False

    def _get_auth_user(self):
        """
        Return the user_id fetched from the auth JWT
        """

        if not hasattr(self.request, 'auth_token'):
            raise APINoAuthToken()

        return self.request.auth_token['aud']

    def handle_request(self):

        # log.debug("Handle Request called!")
        # log.debug(self.request.method)
        # log.debug(self._ENDPOINTS)

        if 'OPTIONS' == self.request.method:
            raise HTTPNoContent(headers=self._cors_headers())

        if self.request.method not in self._ENDPOINTS.keys():
            raise APIMethodNotAllowed('HTTP {} method is not supported by this API endpoint'.format(
                self.request.method))

        self.request_params = RequestParameters(self.request)

        # parse endpoint
        for ep in self._ENDPOINTS[self.request.method]:
            if self._match_endpoint(ep):
                if hasattr(self, ep[1]) and callable(getattr(self, ep[1])):
                    log.debug("Endpoint matched to callable %s", ep[1])
                    self.request.response.headers.update(self._cors_headers())
                    return getattr(self, ep[1])()

        # No endpoints matched, return Bad Request
        raise APIBadRequest()

    def log_debug(self, event_type, message, user_id=None, extra_info=None):
        self._log.debug(APILogRecord(
            request=self.request,
            event_type=event_type,
            user_id=user_id,
            message=message,
            extra_info=extra_info
        ))

    def log_info(self, event_type, message, user_id=None, extra_info=None):
        self._log.info(APILogRecord(
            request=self.request,
            event_type=event_type,
            user_id=user_id,
            message=message,
            extra_info=extra_info
        ))

    def log_warning(self, event_type, message, user_id=None, extra_info=None):
        self._log.warning(APILogRecord(
            request=self.request,
            event_type=event_type,
            user_id=user_id,
            message=message,
            extra_info=extra_info
        ))

    def log_error(self, event_type, message, user_id=None, extra_info=None):
        self._log.error(APILogRecord(
            request=self.request,
            event_type=event_type,
            user_id=user_id,
            message=message,
            extra_info=extra_info
        ))

    def log_critical(self, event_type, message, user_id=None, extra_info=None):
        self._log.critical(APILogRecord(
            request=self.request,
            event_type=event_type,
            user_id=user_id,
            message=message,
            extra_info=extra_info
        ))
