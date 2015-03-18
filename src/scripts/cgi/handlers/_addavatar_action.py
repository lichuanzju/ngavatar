"""This module defines handler that handles add avatar action requests."""


import os
from ng import httpfilters
from ng import str_generator
from ng.database import MySQLDatabase
from ng.excepts import FileWriteError
from ng.http import HttpResponse, HttpRedirectResponse
from ng.models import Avatar
from ng.views import TemplateView
import config
import _accounthelper


def failed_response(account, error_message, conf):
    """Generate add avatar error page with specified error message."""
    template_args = dict(
        error_message=error_message,
        account=account,
        site_name=conf.get('name', '')
    )

    failed_view = TemplateView(
        config.template_filepath('addavatar_failed.html'),
        template_args
    )

    return HttpResponse(failed_view)


def successful_response(account, avatar, conf):
    """Generate response that shows add avatar successful page."""
    template_args = dict(
        account=account,
        avatar=avatar,
        site_name=conf.get('name', '')
    )

    successful_view = TemplateView(
        config.template_filepath('addavatar_successful.html'),
        template_args
    )

    return HttpResponse(successful_view)


@httpfilters.allow_methods('POST')
def handler(request, conf):
    """The handler function."""
    with MySQLDatabase(conf.get('database_connection')) as db:
        # Try to get signed account
        try:
            account = _accounthelper.get_session_account(request, db)
        except _accounthelper.InvalidSessionException as e:
            return e.response

        # Check uploaded file item
        avatar_fileitem = request.field_storage['avatar_file']
        if avatar_fileitem is None or not avatar_fileitem.filename:
            return failed_response(account,
                                   'please choose an image file.',
                                   conf)

        # Get path to the file that should be written in server
        _, file_extension = os.path.split(avatar_fileitem.filename)
        filename = 'avatars/' + str_generator.unique_id() + file_extension
        filepath = config.storage_filepath(filename)

        # Write uploaded file to storage
        try:
            with open(filepath, 'wb') as avatar_file:
                avatar_file.write(avatar_fileitem.file.read())
        except IOError as e:
            raise FileWriteError(filepath)

        # Create avatar instance in database
        avatar = Avatar.create_avatar(db, account, filename)
        if avatar is None:
            # Remove the written file if failed to create
            try:
                os.remove(filepath)
            except OSError as e:
                raise FileWriteError(filename + 'avatars/')

            return failed_response(account,
                                   'cannot add account',
                                   conf)

        return successful_response(account, avatar, conf)
