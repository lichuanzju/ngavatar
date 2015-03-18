"""This module defines handler that handles avatar adding requests."""


from ng import httpfilters
from ng.database import MySQLDatabase
from ng.http import HttpResponse, HttpRedirectResponse
from ng.views import TemplateView
import config
import _accounthelper


def addavatar_response(account, conf):
    """Return response that shows the avatar adding page."""
    template_args = dict(
        account=account,
        site_name=conf.get('name', '')
    )

    addavatar_view = TemplateView(
        config.template_filepath('addavatar.html'),
        template_args
    )

    return HttpResponse(addavatar_view)


@httpfilters.allow_methods('GET')
def handler(request, conf):
    """The handler function."""
    with MySQLDatabase(conf.get('database_connection')) as db:
        # Try to get signed account
        try:
            account = _accounthelper.get_session_account(request, db)
        except _accounthelper.InvalidSessionException as e:
            return e.response

        return addavatar_response(account, conf)
