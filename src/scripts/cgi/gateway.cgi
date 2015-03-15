#!/usr/bin/env python


import cgi
import cgitb
cgitb.enable()
import os
from ng.http import HttpRequest
from ng.http import HttpErrorResponse
from ng.excepts import HttpError
from ng.views import StaticView
import handlers
import config


def response_from_error(error):
    """Get HttpErrorResponse object from HttpError object."""
    # Get error view
    error_page_path = config.static_filepath(
        config.SITE_CONF['error_pages'].get(error.error_code)
    )
    error_view = StaticView(error_page_path)

    # Get error response
    response = HttpErrorResponse(error.error_code, error_view)
    response.add_headers(error.extra_headers)

    return response


def main():
    # Get traceback configuration
    traceback_enabled = config.SITE_CONF['enable_traceback']

    # Enable CGI traceback if needed
    if traceback_enabled:
        cgitb.enable()

    try:
        # Create request from envirioment variables and field storage
        request = HttpRequest(os.environ, cgi.FieldStorage())

        # Get handler for the request
        handler = handlers.handler_for_script(request.script_name)

        # Call handler to generate response and write the response
        response = handler(request, config.SITE_CONF)
        response.write_to_output()
    except HttpError as e:
        # Raise 500 error if traceback enabled
        if traceback_enabled and e.error_code == 500:
            raise e
        else:
            response = response_from_error(e)
            response.write_to_output()
    except Exception as e:
        # Raise unrecognized error if traceback enabled
        if traceback_enabled:
            raise e
        else:
            http_eror = HttpError(500)
            response = response_from_error(http_error)
            response.write_to_output()


if __name__ == '__main__':
    main()
