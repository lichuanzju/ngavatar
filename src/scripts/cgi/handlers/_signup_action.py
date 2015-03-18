"""This module defines the handler that handles sign up action requests."""


from ng.views import TemplateView
from ng.database import MySQLDatabase
from ng.models import Account
from ng.http import HttpResponse
from ng import httpfilters
import config


def failed_response(error_message, conf):
    """Generate sign up error page with specified error message."""
    template_args = dict(
        error_message=error_message,
        site_name=conf.get('name', '')
    )

    failed_view = TemplateView(
        config.template_filepath('signup_failed.html'),
        template_args
    )

    return HttpResponse(failed_view)


def successful_response(account, conf):
    """Generate sign up sucessful page."""
    template_args = dict(
        site_name=conf.get('name', ''),
        username=account.get('username', '')
    )

    successful_view = TemplateView(
        config.template_filepath('signup_successful.html'),
        template_args
    )

    return HttpResponse(successful_view)


@httpfilters.allow_methods('POST')
def handler(request, conf):
    """The handler function."""
    # Get username and password submitted
    username = request.field_storage.getvalue('username')
    password = request.field_storage.getvalue('password')

    # Check username availability
    if not username:
        return failed_response('please input your username', conf)

    # Check password availability
    if not password:
        return failed_response('please input your password', conf)

    # Create account in database
    with MySQLDatabase(conf.get('database_connection')) as db:
        # Check username existance
        if Account.username_exists(db, username):
            return failed_response(
                'username %s already exists' % username,
                conf
            )

        # Create account
        account = Account.create_account(db, username, password)
        if account is None:
            return failed_response('failed to create user account', conf)

        return successful_response(account, conf)
