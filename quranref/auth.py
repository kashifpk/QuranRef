import logging
from pyramid.httpexceptions import HTTPNotFound, HTTPForbidden
from pyramid.urldispatch import _compile_route


from quranref.controllers.exceptions import APIInsufficientPermissions, APIForbidden, APIBadToken
from .lib.jwt import check_auth_header

log = logging.getLogger(__name__)


def authenticator(handler, registry):

    def auth_request(request):

        # ignore static routes for authentication
        if 'static' in request.path.split('/'):
            return handler(request)

        matched_routename = None

        for r in request.registry.introspector.get_category('routes'):
            R = r['introspectable']

            matcher, _ = _compile_route(R['pattern'])

            if isinstance(matcher(request.path), dict):
                matched_routename = R['name']
                break

        # log.debug("Matched route: %s", matched_routename)
        # log.debug(request.path)

        # For API routes do API Auth Token based authentication
        if request.path.startswith('/api/'):

            # log.debug("Is API route")
            # Allow HTTP OPTIONS method for API calls unconditionally
            # if 'OPTIONS' == request.method:
            #     return handler(request)
            # 
            # auth_token = None
            # route_permissions = _get_route_permissions(matched_routename, request.method)
            # log.debug("Route permissions: %r", route_permissions)

            # try:
            #     # Try to get auth token
            #     auth_token = check_auth_header(request)
            #     # log.debug("auth token: %r", auth_token)
            # 
            #     # if we have permissions specified for the route
            #     if route_permissions:
            #         # and we have an auth token
            #         if auth_token:
            #             # Verify the token contains enough permissions to access the resource
            #             # log.info("Permissions %r", auth_token['permissions'])
            #             if not _is_allowed(auth_token['permissions'], matched_routename, request.method):
            #                 return APIInsufficientPermissions("Not enough permissions")
            #         else:
            #             # If the route needs permission(s) but we don't have auth token, return APIForbidden
            #             return APIForbidden()
            # 
            # except APIBadToken as exp:
            #     if route_permissions:
            #         return exp
            # 
            # except Exception as exp:
            #     # If couldn't get auth token and have route permissions, return the appropriate error.
            #     log.error(str(exp))
            #     if route_permissions:
            #         return exp

            # if not route_permissions:
            #     return handler(request)

            return handler(request)

        # Check routes from protected routes here.
        # if not is_allowed(request, matched_routename, request.method):
        #     return HTTPForbidden()

        return handler(request)

    return auth_request
