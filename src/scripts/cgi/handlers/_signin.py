"""This module defines the handler that handlers /signin request."""


from ng.views import TemplateView
from ng.http import HttpResponse
from ng import httpfilters
import config


@httpfilters.allow_methods('GET')
def handler(request, conf):
    """The handler function."""
    username = request.field_storage.getvalue('username', '')

    template_args = dict(
        site_name=conf.get('name', ''),
        username=username
    )

    signin_view = TemplateView(
        config.template_filepath('signin.html'),
        template_args
    )

    return HttpResponse(signin_view)
