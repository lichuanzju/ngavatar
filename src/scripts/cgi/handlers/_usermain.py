"""This module defines handler that handles /user/main requests."""


from ng import httpfilters
from ng.database import MySQLDatabase
from ng.models import Account, Email, Avatar
from ng.http import HttpCookie, HttpResponse, HttpRedirectResponse
from ng.views import TemplateView
import config
import _accounthelper


def usermain_response(db, account, conf):
    """Generate response that shows user main page."""
    uid = account.get('uid')

    emails = Email.load_multiple_from_database(db, owner_uid=uid)
    avatars = Avatar.load_multiple_from_database(db, owner_uid=uid)

    template_args = dict(
        site_name=conf.get('name', ''),
        account=account,
        emails=emails,
        avatars=avatars
    )

    usermain_view = TemplateView(
        config.template_filepath('usermain.html'),
        template_args
    )

    return HttpResponse(usermain_view)


@httpfilters.allow_methods('GET')
def handler(request, conf):
    """The handler function."""
    with MySQLDatabase(conf.get('database_connection')) as db:
        # Try to get the signed in account
        try:
            account = _accounthelper.get_session_account(request, db)
        except _accounthelper.InvalidSessionException as e:
            return e.response

        return usermain_response(db, account, conf)
