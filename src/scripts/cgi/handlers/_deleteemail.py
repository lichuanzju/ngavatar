"""This module defines handler that handles email deleting requests"""


from ng import httpfilters
from ng.database import MySQLDatabase
from ng.http import HttpResponse, HttpRedirectResponse
from ng.models import Email
from ng.views import TemplateView
import config
import _accounthelper


def failed_response(account, error_message, conf):
    """Generate delete email error page with specified error message."""
    template_args = dict(
        error_message=error_message,
        account=account,
        site_name=conf.get('name', '')
    )

    failed_view = TemplateView(
        config.template_filepath('deleteemail_failed.html'),
        template_args
    )

    return HttpResponse(failed_view)


def successful_response(account, email, conf):
    """Generate delete email successful page."""
    template_args = dict(
        site_name=conf.get('name', ''),
        account=account,
        email=email
    )

    successful_view = TemplateView(
        config.template_filepath('deleteemail_successful.html'),
        template_args
    )

    return HttpResponse(successful_view)


@httpfilters.allow_methods('GET', 'POST')
def handler(request, conf):
    """The handler function."""
    with MySQLDatabase(conf.get('database_connection')) as db:
        # Try to get signed account
        try:
            account = _accounthelper.get_session_account(request, db)
        except _accounthelper.InvalidSessionException as e:
            return e.response

        # Get email ID submitted
        emid = int(request.field_storage.getvalue('emid', '-1'))
        if emid < 0:
            return failed_response(account, 'invalid email ID', conf)

        # Load email from database
        email = Email.load_from_database(db,
                                         emid=emid,
                                         owner_uid=account.get('uid'))
        if email is None:
            return failed_response(account, 'invalid email ID', conf)

        # Delete email from database
        if email.delete_from_database(db):
            return successful_response(account, email, conf)
        else:
            return failed_response(
                account,
                'cannot delete email %s' % email.get('email'),
                conf
            )
