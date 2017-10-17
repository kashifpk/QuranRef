"""
JSON Web Tokens Module
=======================

Contains code related to JSON Web Tokens. Allows for verifying a JWT and to confirm that a given JWT
has required permissions etc.

Structure of JWT for API Usage
_______________________________

Each JWT contains the following claims:

**jti**
    JWT's Unique ID

**exp**
    Expiration (int) - The time after which the token is invalid.

**nbf**
    Not Before (int) - The time before which the token is invalid.

**iss**
    Issuer (str) - The principal that issued the JWT.

**aud**
    Audience (str or list(str)) - The recipient that the JWT is intended for.

**iat**
    Issued At 	int 	The time at which the JWT was issued.


A sample JWT may look like::

    {
        "jti": "db7c1c84-08ef-4a30-beca-d90a5aa5cba3",
        "exp": 123213,
        "nbf": 123231,
        "iss": "Threatify Ltd.",
        "aud": "admin",
        "iat": 123124243,
        "permissions": ["premium", "admin"]
    }


"""

import os
import functools
import logging
from jose.exceptions import JWSError, ExpiredSignatureError, JWTClaimsError, JWTError

from ..controllers.exceptions import APINoAuthToken, APIBadToken, APIInvalidToken

log = logging.getLogger(__name__)


def check_auth_header(request):
    """This function encapsulates the logic for checking auth token and raising
    appropriate exceptions"""

    # Ignore HTTP OPTIONS method
    # log.info(request.method)
    if 'OPTIONS' == request.method:
        return

    if 'Authorization' not in request.headers:
        raise APINoAuthToken()

    else:
        # log.debug(request.headers['Authorization'])

        try:
            token_str = request.headers['Authorization'].split(' ')[1]
            # log.debug(token_str)
            # authenticator = JWTRedisAuthenticator.get_authenticator(
            #     request.registry.settings, os.environ['TF_AUTH_PASSWORD'])
            # log.debug("OK: authenticator created")
            # auth_token = authenticator.user_token_from_jwt_string(token_str)
            # log.debug("decoded auth token: %r", auth_token)
            # auth_token.verify()
            # request.auth_token = auth_token.token

            # return auth_token.token
            return token_str

        except IndexError:
            raise APIBadToken()

        except (JWTClaimsError, AssertionError):
            raise APIInvalidToken("auth token claims not valid")

        except ExpiredSignatureError:
            raise APIInvalidToken("Auth token has expired")

        except (JWSError, JWTError):
            raise APIInvalidToken("Auth token signature is invalid")


def auth_verify():
    """
    Decorator for verifying the auth token on a request.
    """
    def _dec(f):
        @functools.wraps(f)
        def wrapper(context, request):
            try:
                check_auth_header(request)
            except Exception as exp:
                return exp

            return f(context, request)

        return wrapper

    return _dec
