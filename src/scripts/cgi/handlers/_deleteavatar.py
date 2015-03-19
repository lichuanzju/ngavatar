"""This module defines handler that handles avatar deleting requests."""


import errno
import os
from ng import httpfilters
from ng.database import MySQLDatabase
from ng.excepts import FileWriteError
from ng.http import HttpResponse, HttpRedirectResponse
from ng.models import Avatar
from ng.views import TemplateView
import config
import _accounthelper


def failed_response(account, error_message, conf):
    """Generate delete avatar error page with specified error message."""
    template_args = dict(
        error_message=error_message,
        account=account,
        site_name=conf.get('name', '')
    )

    failed_view = TemplateView(
        config.template_filepath('deleteavatar_failed.html'),
        template_args
    )

    return HttpResponse(failed_view)


def successful_response(account, conf):
    """Generate response that shows delete avatar successful page."""
    template_args = dict(
        account=account,
        site_name=conf.get('name', '')
    )

    successful_view = TemplateView(
        config.template_filepath('deleteavatar_successful.html'),
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

        # Check aid submitted
        aid = int(request.field_storage.getvalue('aid', -1))
        if aid < 0:
            return failed_response(account, 'invalid avatar ID', conf)

        # Load avatar from database
        avatar = Avatar.load_from_database(db,
                                           aid=aid,
                                           owner_uid=account.get('uid'))
        if avatar is None:
            return failed_response(account, 'invalid avatar ID', conf)

        if not avatar.delete_from_database(db):
            return failed_response(account, 'cannot delete avatar', conf)

        avatar_path = config.storage_filepath(avatar.get('file_path'))
        try:
            os.remove(avatar_path)
        except OSError as e:
            if e.errno != errno.ENOENT:
                raise FileWriteError(avatar_path)

        return successful_response(account, conf)
