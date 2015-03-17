"""This package defines HTTP request handler functions."""


from ng.excepts import HttpError
import _index
import _signup
import _signup_action
import _signin
import _signin_action
import _signout
import _usermain
import _addemail
import _addemail_action
import _addavatar
import _addavatar_action


# Handlers table
_handlers = {
    '/': _index.handler,
    '/signup': _signup.handler,
    '/signup_action': _signup_action.handler,
    '/signin': _signin.handler,
    '/signin_action': _signin_action.handler,
    '/signout': _signout.handler,
    '/user/main': _usermain.handler,
    '/user/addemail': _addemail.handler,
    '/user/addemail_action': _addemail_action.handler,
    '/user/addavatar': _addavatar.handler,
    '/user/addavatar_action': _addavatar_action.handler,
}


def handler_for_script(script_name):
    """Get handler function for the script name of the request."""
    if script_name in _handlers:
        return _handlers[script_name]
    else:
        raise HttpError(404)
