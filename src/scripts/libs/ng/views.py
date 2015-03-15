"""This module defines a series of view classes that generates the body
of HTTP responses."""

import errno
import mimetypes
import os
import sys
from excepts import HttpError
from excepts import FileLocateError
from excepts import FileReadError
from excepts import FileWriteError


class View(object):
    """Empty view."""

    def __init__(self, content_type=None):
        """Create a view with content type."""
        if not content_type:
            self.content_type = 'application/octet-stream'
        else:
            self.content_type = content_type

    def _render_with_file(self, filepath, text_mode):
        """Render the body of this view with specified file.
        text_mode should be True if the file is a text file."""
        # Set file open mode
        if text_mode:
            open_mode = 'r'
        else:
            open_mode = 'rb'

        # Try to read file
        input_file = None
        try:
            input_file = open(filepath, open_mode)
            file_content = input_file.read()
        except IOError as e:
            if e.errno == errno.ENOENT:
                raise FileLocateError(filepath)
            else:
                raise FileReadError(filepath)
        finally:
            if input_file:
                input_file.close()

        return file_content

    def _render_with_text_file(self, filepath):
        """Render the body of this view with a text file."""
        return self._render_with_file(filepath, True)

    def _render_with_binary_file(self, filepath):
        """Render the body of this view with a binary file."""
        return self._render_with_file(filepath, False)

    def _render_body(self):
        """Render the body of this view."""
        return ''

    def write_to_output(self, out=None):
        """Write this view to out file. If out file is not specified,
        stdout is used."""
        if out is None:
            out = sys.stdout

        body = self._render_body()

        out.write(body)
        out.flush()


class StaticView(View):
    """View that displays the content of a static html file."""

    def __init__(self, filepath):
        """Create a static view with path to the html file."""
        View.__init__(self, 'text/html')
        self.filepath = filepath

    def _render_body(self):
        """Render the body of this view with static html file."""
        return self._render_with_text_file(self.filepath)


class ImageView(View):
    """View that displays an image."""

    def __init__(self, image_path, image_format=None):
        """Create an image view with path and format of the image file."""
        # Get image format from path if not given
        if not image_format:
            content_type, _ = mimetypes.guess_type(image_path)
        else:
            content_type = "image/" + image_format

        View.__init__(self, content_type)
        self.filepath = image_path

    def _render_body(self):
        """Render the body of this view with image file."""
        return self._render_with_binary_file(self.filepath)


class BinaryDataView(View):
    """View that send a binary file to client."""

    def __init__(self, filepath, content_type=None):
        """Create binary data view with file path and content type."""
        # Guess content type if not given
        if not content_type:
            content_type = mimetypes.guess_type(filepath)

        View.__init__(self, content_type)
        self.filepath = filepath

        # Get Content-Disposition header from filename
        filename = os.path.basename(filepath)
        self.content_disposition = 'attachment; filename="%s"' % filename

    def _render_body(self):
        """Render the body of this view with binary file."""
        return self._render_with_binary_file(self.filepath)


class TemplateFormatError(HttpError):
    """Error that is raised when format of a template is illegal."""

    def __init__(self, template_filepath, reason=None):
        """Create template format error with path to the file."""
        HttpError.__init__(self, 500)
        self.template_filepath = template_filepath
        self.reason = str(reason)

    def __str__(self):
        """Return description of this error."""
        return 'Template file "%s" has illegal format: %s' %\
            (self.template_filepath, self.reason)


class TemplateView(View):
    """View that displays html loaded from a template."""

    def __init__(self, template_filepath, template_arguments):
        """Create template view with path to template file
        and arguments to evaluate template."""
        View.__init__(self, 'text/html')
        self.filepath = template_filepath
        self.template_arguments = template_arguments

    def _render_body(self):
        """Render the body of this view with template file and arguments."""
        # Load template
        import _template_loader

        try:
            html_string = _template_loader.load_template(
                self.filepath,
                self.template_arguments
            )

            return html_string
        except _template_loader.TemplateSplitError as e:
            raise TemplateFormatError(self.filepath, e)
        except _template_loader.TemplateEvalError as e:
            raise TemplateFormatError(self.filepath, e)


def test_View():
    print 'Emtpy view:'
    empty_view = View()
    empty_view.write_to_output()

    print 'To file:'
    with open('/tmp/view', 'w') as tmp_file:
        empty_view.write_to_output(tmp_file)
    print 'The view has been written to /tmp/view'


def test_StaticView():
    print 'Static View:'

    with open('/tmp/static.html', 'w') as html_file:
        html_file.write("<html>\n</html>")

    static_view = StaticView('/tmp/static.html')
    static_view.write_to_output()


def test_ImageView():
    print "Image View:"

    image_view = ImageView('/tmp/image.png')
    with open('/tmp/imageview', 'wb') as tmp_file:
        image_view.write_to_output(tmp_file)

    print "The view has been written to /tmp/imageview"


def test_BinaryDataView():
    print "Binary Data View:"

    binary_view = BinaryDataView('/tmp/image.png')
    with open('/tmp/binarydataview', 'wb') as tmp_file:
        binary_view.write_to_output(tmp_file)

    print "The view has been written to /tmp/binarydataview"


def test_TemplateView():
    print "Template View:"

    template_arguments = {
        'namespace': 'http://www.w3.org/1999/xhtml',
        'title': 'ngavatar',
        'body': '<h2>Welcome</h2>',
    }
    template_view = TemplateView('/tmp/template.html', template_arguments)
    template_view.write_to_output()


if __name__ == '__main__':
    test_View()
    test_StaticView()
    test_ImageView()
    test_BinaryDataView()
    test_TemplateView()
