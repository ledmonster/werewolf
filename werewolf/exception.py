""" Exceptions """

class APIError(Exception):
    status_code = 400
    error = ""

    def __init__(self, error_description, error=None, status_code=None, payload=None):
        Exception.__init__(self)
        self.error_description = error_description
        if error is not None:
            self.error = error
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['error'] = self.error
        rv['error_description'] = self.error_description
        return rv


class InvalidRequestError(APIError):
    status_code = 400
    error = "invalid_request"


class InvalidClientError(APIError):
    status_code = 401
    error = "invalid_client"


class InvalidGrantError(APIError):
    status_code = 401
    error = "invalid_grant"


class UnauthorizedClientError(APIError):
    status_code = 401
    error = "unauthorized_client"


class UnsupportedGrantTypeError(APIError):
    status_code = 400
    error = "unsupported_grant_type"


class InvalidScopeError(APIError):
    status_code = 400
    error = "invalid_scope"


class NotFoundError(APIError):
    status_code = 404
    error = "not_found"


class ServerError(APIError):
    status_code = 500
    error = "server_error"


class GameException(Exception):
    pass
