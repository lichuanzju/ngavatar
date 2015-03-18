"""This module provides utility functions for loading templates."""


import errno
import contextlib
import sys
from cStringIO import StringIO
from excepts import NGError
from excepts import FileLocateError
from excepts import FileReadError


class TemplateSplitError(NGError):
    """Error that is raised when unable to split template string."""

    def __init__(self, reason):
        """Create template split error with specified reason."""
        self.reason = str(reason)

    def __str__(self):
        """Return description of this error."""
        return self.reason


class TemplateEvalError(NGError):
    """Error that is raised when unable to evaluate template string."""

    def __init__(self, template_string):
        """Create template eval error with the template string."""
        self.template_string = template_string

    def __str__(self):
        """Return description of this error."""
        return 'Can\'t evaluate "%s"' % self.template_string


@contextlib.contextmanager
def _stdoutIO(out=None):
    """Context manager that replaces stdout with StringIO within context."""
    # Save stdout
    old = sys.stdout

    # Replace stdout with StringIO
    if out is None:
        out = StringIO()
    sys.stdout = out

    # Return StringIO object
    yield out

    # Restore stdout
    sys.stdout = old


def _split_template(template_string):
    """Split template content to html parts and python parts."""
    # Create sequence that stores the result parts of the split
    parts = []

    # Initialize parameters
    length = len(template_string)
    start = 0
    py_start = 0
    py_end = 0

    # Search for split signs until reaches the end
    while start < length:
        # Find the start sign
        py_start = template_string.find('{%', start)
        # If not found, add the remaining substring to result and stop
        if py_start < 0:
            parts.append(template_string[start:length])
            break

        # Find the end sign
        py_end = template_string.find('%}', py_start + 2)
        # If not found, raise split error
        if py_end < 0:
            raise TemplateSplitError('Tags don\'t match')

        # Both start and end signs are found, add html and python parts to
        # resut
        parts.append(template_string[start:py_start])
        parts.append(template_string[(py_start + 2):py_end].strip())

        # Reset search position
        start = py_end + 2

    return parts


def _eval_py(py_part, template_variables):
    """Evaluate a python part with given variables."""
    try:
        with _stdoutIO() as s:
            exec(py_part, template_variables, {})
        return s.getvalue()
    except Exception as e:
        raise TemplateEvalError(py_part)


def _eval_template(template_string, template_args):
    """Evaluate template string with specified arguments."""
    parts = _split_template(template_string)

    # Evaluate python parts(parts with odd indexes) and replace it with the
    # result
    for py_index in range(1, len(parts), 2):
        parts[py_index] = _eval_py(parts[py_index], template_args)

    return ''.join(parts)


def load_template(template_filepath, template_args):
    """Load template file from specified path and
    evaluate it with specified arguments."""
    # Read content of the template file
    template_file = None
    try:
        template_file = open(template_filepath, 'r')
        template_content = template_file.read()
    except IOError as e:
        if e.errno == errno.ENOENT:
            raise FileLocateError(template_filepath)
        else:
            raise FileReadError(template_filepath)
    finally:
        if template_file:
            template_file.close()

    return _eval_template(template_content, template_args)


def test_split():
    with open('/tmp/template.html', 'r') as template_file:
        template_string = template_file.read()

    try:
        print _split_template(template_string)
    except TemplateSplitError as e:
        print e


def test_load():
    template_args = {
        'title': 'ngavatar',
        'body': 'Welcome',
        'namespace': '<w3c>',
    }

    print load_template("/tmp/template.html", template_args)
    print template_args.keys()


def test_eval():
    pystr = 'print a'
    print _eval_py(pystr, {'a': 1})


if __name__ == '__main__':
    print "Eval Test:"
    test_eval()

    print "Split Test:"
    test_split()

    print "\nLoad test:"
    test_load()
