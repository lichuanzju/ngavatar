"""This module defines the handler that handles avatar set requests."""


from ng import httpfilters
from ng.database import MySQLDatabase
from ng.models import Account, Email, Avatar
from ng.http import HttpCookie, HttpResponse, HttpRedirectResponse
from ng.views import TemplateView
import config
import _accounthelper


def failed_response(account, error_message, conf):
    """Generate response that shows a page with error message."""
    template_args = dict(
        error_message=error_message,
        account=account,
        site_name=conf.get('name', '')
    )

    failed_view = TemplateView(
        config.template_filepath('setavatar_error.html'),
        template_args
    )

    return HttpResponse(failed_view)


def setavatar_response(db, account, email, conf):
    """Generate response that shows avatar setting page."""
    avatars = Avatar.load_multiple_from_database(
        db,
        owner_uid=account.get('uid'))

    if not avatars:
        return failed_response(account, 'please add avatars first', conf)

    template_args = dict(
        account=account,
        email=email,
        avatars=avatars,
        site_name=conf.get('name', '')
    )

    setavatar_view = TemplateView(
        config.template_filepath('setavatar.html'),
        template_args
    )

    return HttpResponse(setavatar_view)


@httpfilters.allow_methods('GET')
def handler(request, conf):
    """The handler function."""
    with MySQLDatabase(conf.get('database_connection')) as db:
        # Try to get the signed in account
        account_or_response = _accounthelper.check_signed_in(request, db)
        if isinstance(account_or_response, HttpResponse):
            return account_or_response
        account = account_or_response

        # Check the email id from the query string
        emid = int(request.field_storage.getvalue('emid', 0))
        if not emid:
            return failed_response(account,
                                   'please select an email address',
                                   conf)

        # Load the email instance from database
        email = Email.load_from_database(db,
                                         owner_uid=account.get('uid'),
                                         emid=emid)
        if email is None:
            return failed_response(account,
                                   'cannot find email address',
                                   conf)

        return setavatar_response(db, account, email, conf)
