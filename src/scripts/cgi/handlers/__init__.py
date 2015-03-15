"""This package defines HTTP request handler functions."""


from ng.excepts import HttpError
from ng.httpfilters import method_checker
from ng.http import HttpResponse
from ng.views import StaticView
import config


@method_checker('GET')
def index_handler(request, conf):
    index_view = StaticView(config.static_filepath('index.html'))
    return HttpResponse(index_view)


# Handlers table
_handlers = {
    '/': index_handler,
}


def handler_for_script(script_name):
    """Get handler function for the script name of the request."""
    if script_name in _handlers:
        return _handlers[script_name]
    else:
        raise HttpError(404)
