"""This module defines decorators that filter HTTP requests for request
handlers"""


from excepts import HttpError


def method_checker(*http_methods):
    """Filter that checks whether the method of the HTTP request is
    supported."""
    def method_checker_decorator(handler):
        """The real decorator."""
        def method_checker_wrapper(request, *args):
            """Wrapper function."""
            if request.method not in http_methods:
                allow_header = str(http_methods)[1:-1]
                raise HttpError(405, Allow=allow_header)

            return handler(request, *args)

        return method_checker_wrapper

    return method_checker_decorator
