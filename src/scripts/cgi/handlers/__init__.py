"""This package defines HTTP request handler functions."""


from ng.excepts import HttpError
import _index

# Handlers table
_handlers = {
    '/': _index.handler,
}


def handler_for_script(script_name):
    """Get handler function for the script name of the request."""
    if script_name in _handlers:
        return _handlers[script_name]
    else:
        raise HttpError(404)
