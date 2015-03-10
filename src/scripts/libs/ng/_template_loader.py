"""This module provides utility functions for loading templates."""


from excepts import NGError
from excepts import TemplateFormatError


class _TemplateSplitError(NGError):
    """Error that is raised when unable to split template string"""

    def __init__(self, reason):
        """Create template split error with specified reason."""
        self.reason = reason

    def __str__(self):
        """Return description of this error."""
        return str(self.reason)


class _TemplateEvalError(NGError):
    """Error that is raised when unable to evaluate template string"""

    def __init__(self, template_string):
        """Create template eval error with the template string"""
        self.template_string = template_string

    def __str__(self):
        """Return description of this error."""
        return 'Can\'t evaluate "%s"' % self.template_string


def _split_template(template_string):
    """Split template content to html parts and python parts"""
    parts = []

    length = len(template_string)
    start = 0
    py_start = 0
    py_end = 0

    while start < length:
        py_start = template_string.find('{%', start)
        if py_start < 0:
            parts.append(template_string[start:length])
            break

        py_end = template_string.find('%}', py_start + 2)
        if py_end < 0:
            raise _TemplateSplitError('Tags don\'t match')

        parts.append(template_string[start:py_start])
        parts.append(template_string[(py_start + 2):py_end].strip())

        start = py_end + 2

    return parts


def _eval_py(py_part, template_args):
    """Evaluate a python part with specified arguments"""
    global_ = template_args
    global_['_result_'] = ''

    try:
        exec(py_part, global_)
    except:
        raise _TemplateEvalError(py_part)

    return global_['_result_']


def _eval_template(template_string, template_args):
    """Evaluate template string with specified arguments"""
    parts = _split_template(template_string)

    for py_index in range(1, len(parts), 2):
        parts[py_index] = _eval_py(parts[py_index], template_args)

    return ''.join(parts)


def load_template(template_filepath, template_args):
    """Load template file from specified path and
    evaluate it with specified arguments."""
    with open(template_filepath, 'r') as template_file:
        template_content = template_file.read()

    try:
        return _eval_template(template_content, template_args)
    except _TemplateSplitError as split_error:
        raise TemplateFormatError(template_filepath, split_error.reason)
    except _TemplateEvalError as eval_error:
        raise TemplateFormatError(template_filepath, str(eval_error))

def test_split():
    with open('/tmp/template.html', 'r') as template_file:
        template_string = template_file.read()

    try:
        print _split_template(template_string)
    except _TemplateSplitError as e:
        print e


def test_load():
    template_args = {
        'title': 'ngavatar',
        'body': 'Welcome',
        'namespace': '<w3c>',
    }

    print load_template("/tmp/template.html", template_args)


if __name__ == '__main__':
    print "Split Test:"
    test_split()

    print "\nLoad test:"
    test_load()
