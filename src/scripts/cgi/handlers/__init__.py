"""This package defines HTTP request handler functions."""


from ng.excepts import HttpError
import _index
import _signup
import _signup_action
import _signin
import _signin_action
import _signout
import _usermain


# Handlers table
_handlers = {
    '/': _index.handler,
    '/signup': _signup.handler,
    '/signup_action': _signup_action.handler,
    '/signin': _signin.handler,
    '/signin_action': _signin_action.handler,
    '/signout': _signout.handler,
    '/user/main': _usermain.handler,
}


def handler_for_script(script_name):
    """Get handler function for the script name of the request."""
    if script_name in _handlers:
        return _handlers[script_name]
    else:
        raise HttpError(404)
