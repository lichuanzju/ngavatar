"""This module defines handler that handles the /index request."""


from ng.views import TemplateView
from ng.http import HttpResponse
from ng import httpfilters
import config


@httpfilters.method_checker('GET')
def handler(request, conf):
    """The handler function."""
    template_args = dict(
        page_name='Welcome',
        site_name=conf.get('name', '')
    )

    index_view = TemplateView(
        config.template_filepath('index.html'),
        template_args
    )

    return HttpResponse(index_view)
