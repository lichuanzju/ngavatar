"""This module defines decorators that filter HTTP requests for request
handlers"""


from excepts import HttpError


def allow_methods(*http_methods):
    """Filter that checks whether the method of the HTTP request is
    supported."""
    def allow_methods_decorator(handler):
        """The real decorator."""
        def allow_methods_wrapper(request, *args):
            """Wrapper function."""
            if request.method not in http_methods:
                allow_header = str(http_methods)[1:-1]
                raise HttpError(405, Allow=allow_header)

            return handler(request, *args)

        return allow_methods_wrapper

    return allow_methods_decorator
