"""This module defines handler that handles the /index request."""


from ng.views import StaticView
from ng.http import HttpResponse
from ng import httpfilters
import config


@httpfilters.method_checker('GET')
def handler(request, conf):
    """The handler function."""
    index_view = StaticView(config.static_filepath('index.html'))
    return HttpResponse(index_view)
