"""This package defines HTTP request handler functions."""


from ng.excepts import HttpError
import _index
import _signup
import _favicon
import _signup_action
import _signin
import _signin_action


# Handlers table
_handlers = {
    '/': _index.handler,
    '/favicon.ico': _favicon.handler,
    '/signup': _signup.handler,
    '/signup_action': _signup_action.handler,
    '/signin': _signin.handler,
    '/signin_action': _signin_action.handler,
}


def handler_for_script(script_name):
    """Get handler function for the script name of the request."""
    if script_name in _handlers:
        return _handlers[script_name]
    else:
        raise HttpError(404)
