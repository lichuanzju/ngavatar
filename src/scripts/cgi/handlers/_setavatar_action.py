"""This module defines the handler that handles avatar setting action
requests."""


from ng import httpfilters
from ng.database import MySQLDatabase
from ng.http import HttpResponse, HttpRedirectResponse
from ng.models import Account, Email, Avatar
from ng.views import TemplateView
import config
import _accounthelper


def failed_response(account, error_message, conf):
    """Generate set avatar error page with specified error message."""
    template_args = dict(
        error_message=error_message,
        account=account,
        site_name=conf.get('name', '')
    )

    failed_view = TemplateView(
        config.template_filepath('setavatar_failed.html'),
        template_args
    )

    return HttpResponse(failed_view)


def successful_response(account, email, avatar, conf):
    """Generate set avatar successful page."""
    template_args = dict(
        account=account,
        email=email,
        avatar=avatar,
        site_name=conf.get('name', '')
    )

    successful_view = TemplateView(
        config.template_filepath('setavatar_successful.html'),
        template_args
    )

    return HttpResponse(successful_view)


def remove_avatar_response(account, email, conf):
    """Generate remove avatar successful page."""
    template_args = dict(
        account=account,
        email=email,
        site_name=conf.get('name', '')
    )

    remove_view = TemplateView(
        config.template_filepath('removeavatar_successful.html'),
        template_args
    )

    return HttpResponse(remove_view)


@httpfilters.allow_methods('POST')
def handler(request, conf):
    """The handler function."""
    with MySQLDatabase(conf.get('database_connection')) as db:
        # Try to get signed account
        account_or_response = _accounthelper.check_signed_in(request, db)
        if isinstance(account_or_response, HttpResponse):
            return account_or_response
        account = account_or_response

        # Check email id submitted
        emid = int(request.field_storage.getvalue('emid', 0))
        if not emid:
            return failed_response(account, 'invalid email ID', conf)

        # Check email in database
        email = Email.load_from_database(db,
                                         owner_uid=account.get('uid'),
                                         emid=emid)
        if email is None:
            return failed_response(account, 'cannot find email', conf)

        # Check avatar id submitted
        aid = int(request.field_storage.getvalue('aid', 0))
        if not aid:
            return failed_response(account, 'invalid avatar ID', conf)

        # Check whether needed to remove the avatar binding
        if aid < 0:
            email['avatar_id'] = None
            if email.update_to_database(db, 'avatar_id'):
                return remove_avatar_response(account, email, conf)
            else:
                return failed_response(
                    account,
                    'cannot remove avatar from email %s' % email.get('email'),
                    conf)

        # Check avatar in database
        avatar = Avatar.load_from_database(db,
                                           owner_uid=account.get('uid'),
                                           aid=aid)
        if avatar is None:
            return failed_response(account, 'cannot find avatar', conf)

        # Set the avatar to the email
        email['avatar_id'] = aid
        if not email.update_to_database(db, 'avatar_id'):
            return failed_response(account,
                                   'cannot set this avatar for the email',
                                   conf)

        return successful_response(account, email, avatar, conf)
