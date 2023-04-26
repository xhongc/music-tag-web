import mimetypes
from os.path import splitext

from django.core import validators
from django.core.exceptions import ValidationError
from django.core.files.images import get_image_dimensions
from django.template.defaultfilters import filesizeformat
from django.utils.deconstruct import deconstructible
from django.utils.translation import ugettext_lazy as _


@deconstructible
class ImageDimensionsValidator:
    """
    ImageField dimensions validator.

    from https://gist.github.com/emilio-rst/4f81ea2718736a6aaf9bdb64d5f2ea6c
    """

    def __init__(
        self,
        width=None,
        height=None,
        min_width=None,
        max_width=None,
        min_height=None,
        max_height=None,
    ):
        """
        Constructor

        Args:
            width (int): exact width
            height (int): exact height
            min_width (int): minimum width
            min_height (int): minimum height
            max_width (int): maximum width
            max_height (int): maximum height
        """

        self.width = width
        self.height = height
        self.min_width = min_width
        self.max_width = max_width
        self.min_height = min_height
        self.max_height = max_height

    def __call__(self, image):
        w, h = get_image_dimensions(image)

        if self.width is not None and w != self.width:
            raise ValidationError(_("Width must be %dpx.") % (self.width,))

        if self.height is not None and h != self.height:
            raise ValidationError(_("Height must be %dpx.") % (self.height,))

        if self.min_width is not None and w < self.min_width:
            raise ValidationError(_("Minimum width must be %dpx.") % (self.min_width,))

        if self.min_height is not None and h < self.min_height:
            raise ValidationError(
                _("Minimum height must be %dpx.") % (self.min_height,)
            )

        if self.max_width is not None and w > self.max_width:
            raise ValidationError(_("Maximum width must be %dpx.") % (self.max_width,))

        if self.max_height is not None and h > self.max_height:
            raise ValidationError(
                _("Maximum height must be %dpx.") % (self.max_height,)
            )


@deconstructible
class FileValidator:
    """
    Taken from https://gist.github.com/jrosebr1/2140738
    Validator for files, checking the size, extension and mimetype.
    Initialization parameters:
        allowed_extensions: iterable with allowed file extensions
            ie. ('txt', 'doc')
        allowd_mimetypes: iterable with allowed mimetypes
            ie. ('image/png', )
        min_size: minimum number of bytes allowed
            ie. 100
        max_size: maximum number of bytes allowed
            ie. 24*1024*1024 for 24 MB
    Usage example::
        MyModel(models.Model):
            myfile = FileField(validators=FileValidator(max_size=24*1024*1024), ...)
    """

    extension_message = _(
        "Extension '%(extension)s' not allowed. Allowed extensions are: '%(allowed_extensions)s.'"
    )
    mime_message = _(
        "MIME type '%(mimetype)s' is not valid. Allowed types are: %(allowed_mimetypes)s."
    )
    min_size_message = _(
        "The current file %(size)s, which is too small. The minimum file size is %(allowed_size)s."
    )
    max_size_message = _(
        "The current file %(size)s, which is too large. The maximum file size is %(allowed_size)s."
    )

    def __init__(self, *args, **kwargs):
        self.allowed_extensions = kwargs.pop("allowed_extensions", None)
        self.allowed_mimetypes = kwargs.pop("allowed_mimetypes", None)
        self.min_size = kwargs.pop("min_size", 0)
        self.max_size = kwargs.pop("max_size", None)

    def __call__(self, value):
        """
        Check the extension, content type and file size.
        """

        # Check the extension
        ext = splitext(value.name)[1][1:].lower()
        if self.allowed_extensions and ext not in self.allowed_extensions:
            message = self.extension_message % {
                "extension": ext,
                "allowed_extensions": ", ".join(self.allowed_extensions),
            }

            raise ValidationError(message)

        # Check the content type
        mimetype = mimetypes.guess_type(value.name)[0]
        if self.allowed_mimetypes and mimetype not in self.allowed_mimetypes:
            message = self.mime_message % {
                "mimetype": mimetype,
                "allowed_mimetypes": ", ".join(self.allowed_mimetypes),
            }

            raise ValidationError(message)

        # Check the file size
        filesize = len(value)
        if self.max_size and filesize > self.max_size:
            message = self.max_size_message % {
                "size": filesizeformat(filesize),
                "allowed_size": filesizeformat(self.max_size),
            }

            raise ValidationError(message)

        elif filesize < self.min_size:
            message = self.min_size_message % {
                "size": filesizeformat(filesize),
                "allowed_size": filesizeformat(self.min_size),
            }

            raise ValidationError(message)


class DomainValidator(validators.URLValidator):
    message = "Enter a valid domain name."

    def __call__(self, value):
        """
        This is a bit hackish but since we don't have any built-in domain validator,
        we use the url one, and prepend http:// in front of it.

        If it fails, we know the domain is not valid.
        """
        super().__call__(f"http://{value}")
        return value
