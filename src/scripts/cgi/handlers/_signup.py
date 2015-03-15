"""This module defines the handler that handlers /signup request."""


from ng.views import TemplateView
from ng.http import HttpResponse
from ng import httpfilters
import config


@httpfilters.method_checker('GET')
def handler(request, conf):
    """The handler function."""
    template_args = dict(
        site_name=conf.get('name', '')
    )

    signup_view = TemplateView(
        config.template_filepath('signup.html'),
        template_args
    )

    return HttpResponse(signup_view)
