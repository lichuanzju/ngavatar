"""This module defines handler that handlers action of adding email."""


import re
from ng import httpfilters
from ng.database import MySQLDatabase
from ng.http import HttpResponse, HttpRedirectResponse
from ng.models import Email
from ng.views import TemplateView
import config
import _accounthelper


def failed_response(account, error_message, conf):
    """Generate add email error page with specified error message."""
    template_args = dict(
        error_message=error_message,
        account=account,
        site_name=conf.get('name', '')
    )

    failed_view = TemplateView(
        config.template_filepath('addemail_failed.html'),
        template_args
    )

    return HttpResponse(failed_view)


def successful_response(account, email, conf):
    """Generate add email successful page."""
    template_args = dict(
        site_name=conf.get('name', ''),
        account=account,
        email=email
    )

    successful_view = TemplateView(
        config.template_filepath('addemail_successful.html'),
        template_args
    )

    return HttpResponse(successful_view)


def check_email_format(email):
    """Use regular expression to check the format of the email. Return
    whether the parameter is a legal email address."""
    return re.match('^(\w)+(\.\w+)*@(\w)+((\.\w+)+)$', email) is not None

@httpfilters.allow_methods('POST')
def handler(request, conf):
    """The handler function."""
    with MySQLDatabase(conf.get('database_connection')) as db:
        # Try to get signed account
        try:
            account = _accounthelper.get_session_account(request, db)
        except _accounthelper.InvalidSessionException as e:
            return e.response

        # Check email submitted
        email_addr = request.field_storage.getvalue('email')
        if not email_addr:
            return failed_response(account,
                                   'please input your email address',
                                   conf)

        # Check email format
        if not check_email_format(email_addr):
            return failed_response(
                account,
                '%s is not a valid email address' % email_addr,
                conf
            )

        # Check email existance
        if Email.email_exists(db, email_addr):
            return failed_response(account,
                                   'email %s already exists' % email_addr,
                                   conf)

        # Create email
        email = Email.create_email(
            db,
            account,
            email_addr,
        )

        # Check email creation
        if email is None:
            return failed_response(account,
                                   'cannot add email',
                                   conf)

        return successful_response(account, email, conf)
