"""This module defines a series of views that generates HTTP responses."""

import sys
import os
import errno
from excepts import FileLocateError
from excepts import FileReadError
from excepts import FileWriteError


class View(object):
    """Empty view that only contains headers."""

    def __init__(self, headers=None):
        """Create an empty view with extra headers."""
        self.headers = {'Content-Type': "text/plain"}
        if headers:
            self._add_headers(headers)

    def _add_headers(self, headers):
        """Add extra headers to self.headers."""
        for key, value in headers.items():
            # If the value is a list, add it to the original list
            if isinstance(value, list):
                if key in self.headers:
                    self.headers[key] = self.headers[key] + value
                else:
                    self.headers[key] = value
            else:
                self.headers[key] = value

    def add_headers(self, headers):
        """Add extra headers to this view."""
        if headers:
            self._add_headers(headers)

    def remove_header(self, header_name):
        """Remove the specified header from this view."""
        if header_name in self.headers:
            del self.headers[header_name]

    def _write_headers(self, out):
        """Write headers of this view to output file."""
        # Construct header string
        header_list = []
        for key, value in self.headers.items():
            # If there is multiple values for one key,
            # create item for each value
            if isinstance(value, list):
                for item in value:
                    header_list.append('%s: %s' % (key, item))
            else:
                header_list.append('%s: %s' % (key, value))
        headers_str = '\r\n'.join(header_list)

        # write header string to output file
        try:
            out.write(headers_str)
            out.write('\r\n\r\n')
            out.flush()
        except IOError as e:
            raise FileWriteError(out.name)

    def _write_file(self, filepath, text_mode, out):
        """Write a file with specified path to output.
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

        # Try to write file
        try:
            out.write(file_content)
            out.flush()
        except IOError as e:
            raise FileWriteError(out.name)

    def _write_text_file(self, filepath, out):
        """Write a text file with specified path to output."""
        self._write_file(filepath, True, out)

    def _write_binary_file(self, filepath, out):
        """Write a binary file with specified path to output."""
        self._write_file(filepath, False, out)

    def write_to_output(self, out=None):
        """Write this view to output. out is the specified output file.
        If out is not specified, stdout will be used."""
        # Use stdout if output file is not specified
        if not out:
            out = sys.stdout

        self._write_headers(out)


class StaticView(View):
    """View that displays the content of a static html file."""

    def __init__(self, filepath):
        """Create a static view with path to the html file."""
        self.headers = {'Content-Type': 'text/html'}
        self.filepath = filepath

    def write_to_output(self, out=None):
        """Write headers and content of the static html file to output.
        If out is not specified, stdout will be used."""
        if not out:
            out = sys.stdout

        # Write headers
        self._write_headers(out)

        # Write content of the static file
        self._write_text_file(self.filepath, out)


class ImageView(View):
    """View that displays an image."""

    def __init__(self, image_path, image_format=None):
        """Create an image view with path and format of the image file."""
        self.filepath = image_path

        if not image_format:
            file_extension = os.path.splitext(image_path)[1]
            if not file_extension:
                file_extension = 'jpeg'

            import _image_extension_to_format
            image_format = _image_extension_to_format.\
                image_format_from_extension(file_extension)

        content_type = "image/" + image_format
        self.headers = {'Content-Type': content_type}

    def write_to_output(self, out=None):
        """Write this image view to output.
        If out is not specified, stdout will be used."""
        if not out:
            out = sys.stdout

        # Write headers
        self._write_headers(out)

        # Write image file
        self._write_binary_file(self.filepath, out)


class BinaryDataView(View):
    """View that send a binary file to client."""

    def __init__(self, filepath):
        """Create a binary data view with path to the binary file."""
        self.filepath = filepath

        # Get Content-Disposition header from filename
        filename = os.path.basename(filepath)
        content_disposition = 'attachment; filename="%s"' % filename

        self.headers = {
            'Content-Type': 'application/octet-stream',
            'Content-Disposition': content_disposition,
        }

    def write_to_output(self, out=None):
        """Write this binary data view to output.
        If out is not specified, stdout will be used."""
        if not out:
            out = sys.stdout

        # Write headers
        self._write_headers(out)

        # Write binary file
        self._write_binary_file(self.filepath, out)


class TemplateView(View):
    """View that displays html loaded from a template."""

    def __init__(self, template_filepath, template_arguments):
        """Create template view with path to template file
        and arguments to evaluate template."""
        self.filepath = template_filepath
        self.headers = {'Content-Type': 'text/html'}
        self.template_arguments = template_arguments

    def write_to_output(self, out=None):
        """Load this template view and write this template view to output.
        If out is not specified, stdout will be used."""
        if not out:
            out = sys.stdout

        # Write headers
        self._write_headers(out)

        # Load template
        import _template_loader
        html_string = _template_loader.load_template(
            self.filepath,
            self.template_arguments
        )

        # Write html string
        try:
            out.write(html_string)
            out.flush()
        except IOError as e:
            raise FileWriteError(out.name)


def test_View():
    print 'Emtpy view:'
    empty_view = View()
    empty_view.write_to_output()

    print 'Header view:'
    header_view = View({
            'Content-Type': "text/html",
            'Content-Length': '123',
        })
    header_view.add_headers({'Set-Cookie': ['ID=1', 'Session=foo']})
    header_view.remove_header('Content-Length')
    header_view.write_to_output()

    print 'To file:'
    with open('/tmp/view', 'w') as tmp_file:
        header_view.write_to_output(tmp_file)
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

    binary_view = BinaryDataView('/tmp/data.bin')
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
    # test_View()
    # test_StaticView()
    # test_ImageView()
    # test_BinaryDataView()
    test_TemplateView()
