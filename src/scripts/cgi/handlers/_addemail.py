"""This module defines handler that handles add email requests."""


from ng import httpfilters
from ng.database import MySQLDatabase
from ng.http import HttpResponse, HttpRedirectResponse
from ng.views import TemplateView
import config
import _accounthelper


def addemail_response(account, conf):
    """Return response that shows the email adding page."""
    template_args = dict(
        site_name=conf.get('name', ''),
        account=account
    )

    addemail_view = TemplateView(
        config.template_filepath('addemail.html'),
        template_args
    )

    return HttpResponse(addemail_view)


@httpfilters.allow_methods('GET')
def handler(request, conf):
    """The handler function."""
    with MySQLDatabase(conf.get('database_connection')) as db:
        # Try to get signed account
        account_or_response = _accounthelper.check_signed_in(request, db)
        if isinstance(account_or_response, HttpResponse):
            return account_or_response

        account = account_or_response
        return addemail_response(account, conf)
