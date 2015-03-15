"""This module defines handler that handles favicon.ico requests."""


from ng.views import ImageView
from ng.http import HttpResponse
from ng import httpfilters
import config


@httpfilters.allow_methods('GET')
def handler(request, conf):
    """The handler function."""
    icon_view = ImageView(
        config.static_filepath('icons/favicon.ico')
    )

    return HttpResponse(icon_view)
