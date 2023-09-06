#!/usr/bin/env python

from collections import namedtuple
import hashlib
import io
import shutil

import mutagen
from mutagen.id3 import PictureType
try:
    import PIL
    from PIL import Image
    BICUBIC = PIL.Image.BICUBIC
    _HAS_PIL = True
except ImportError:
    BICUBIC = None
    _HAS_PIL = False

from component.music_tag import util


def getter_not_implemented(afile, norm_key):
    raise NotImplementedError("getter: '{0}' not implemented for {1}"
                              "".format(norm_key, type(afile)))

def setter_not_implemented(afile, norm_key, val):
    raise NotImplementedError("setter: '{0}' not implemented for {1}"
                              "".format(norm_key, type(afile)))

def albumartist_from_comp(afile, norm_key):
    ret = None
    if afile.get('compilation', default=None):
        ret = 'Various Artists'
    return ret

def comp_from_albumartist(afile, norm_key):
    ret = None
    albumartist = afile.get('albumartist', default=None)
    if albumartist:
        albumartist = albumartist.first.lower().replace(' ', '')
        if albumartist in ('various', 'variousartists'):
            ret = True
        else:
            ret = False
    return ret


TAG_MAP_ENTRY = namedtuple('TAG_MAP_ENTRY', ('getter', 'setter', 'remover',
                                             'type', 'sanitizer'))
TAG_MAP_ENTRY.__new__.__defaults__ = (getter_not_implemented,  # getter
                                      setter_not_implemented,  # setter
                                      None,  # remover
                                      str,  # type
                                      None,  # sanitizer
                                      )


class MetadataItem(object):
    def __init__(self, typ, sanitizer, val):
        self._values = None

        if isinstance(val, MetadataItem):
            val = val.values

        self.type = typ
        self.sanitizer = sanitizer
        self.values = val

    @property
    def ismissing(self):
        return bool(self.values)
    @property
    def isna(self):
        return bool(self.values)

    @property
    def values(self):
        return self._values
    @values.setter
    def values(self, val):
        if isinstance(val, (list, tuple)):
            self._values = list(val)
        elif val is None:
            self._values = []
        else:
            self._values = [val]

        for i, v in enumerate(self._values):
            if self.sanitizer is not None:
                v = self.sanitizer(v)
            if not (self.type is None or v is None or isinstance(v, self.type)):
                v = self.type(v)
            self._values[i] = v

    @property
    def value(self):
        try:
            if self.type is None:
                if len(self.values) == 1:
                    val = self.values[0]
                else:
                    val = str(self)
            else:
                val = self.type(self)
        except TypeError:
            values = self.values
            if not values:
                raise ValueError("No values exist")
            elif len(values) > 1:
                raise ValueError("Multiple values exist: {0}".format(repr(values)))
            val = values[0]
        return val
    @property
    def val(self):
        return self.value

    @property
    def first(self):
        try:
            return self._values[0]
        except IndexError:
            return None

    def append(self, val):
        if self.sanitizer is not None:
            val = self.sanitizer(val)
        if not (self.type is None or val is None or isinstance(val, self.type)):
            val = self.type(val)

        if self._values:
            self._values.append(val)
        else:
            self._values = [val]

    def __len__(self):
        return len(self._values)

    def __str__(self):
        return ', '.join(str(li) for li in self._values)

    def __int__(self):
        if not self._values:
            val = 0
        elif len(self._values) == 1:
            val = int(self._values[0])
        else:
            raise ValueError("Metadata must have 1 value to cast to int")
        return val

    def __bool__(self):
        return any(self._values)

    def __list__(self):
        return list(self._values)

    def __tuple__(self):
        return tuple(self._values)

    def __repr__(self):
        return '<MetadataItem: {0}>'.format(self.__str__())


class Artwork(object):
    def __init__(self, raw, width=None, height=None, fmt=None, depth=None,
                 pic_type=PictureType.COVER_FRONT):
        if isinstance(raw, Artwork):
            orig = raw
            raw = orig.raw
            width, height = orig.width, orig.height
            fmt, depth = orig.fmt, orig.depth
            pic_type = orig.pic_type
            del orig

        if not isinstance(raw, bytes):
            raise TypeError("image data must have type 'bytes'")

        self.raw = raw

        if any(v is None for v in (width, height, fmt, depth)):
            try:
                img = self.image
                width = img.width
                height = img.height
                fmt = img.format.lower()
                mode2depth = {'1': 1, 'L': 8, 'P': 8, 'RGB': 24, 'RGBA': 32,
                              'CMYK': 32, 'YCbCr': 24, 'I': 32, 'F': 32}
                depth = mode2depth[img.mode]
            except ImportError:
                width = None
                height = None
                fmt = None
                depth = None

        self.width = width
        self.height = height
        self.depth = depth
        self.format = fmt
        self.mime = "image/{0}".format(self.format)

        # ``pic_type`` should be one of ``mutagen.id3.PictureType.*``
        self.pic_type = pic_type

        # Image.open(io.BytesIO(self.data))  # for testing

    @property
    def data(self):
        return self.raw

    @property
    def image(self):
        img = None
        if _HAS_PIL:
            img = Image.open(io.BytesIO(self.raw))
        else:
            raise ImportError("PIL (Pillow) not installed")
        return img

    def thumbnail(self, size, method=BICUBIC):
        image = self.image
        image.thumbnail(size, method)
        return image

    def raw_thumbnail(self, size, method=BICUBIC, format=None, quality=95,
                      return_info=False):
        thumb = self.thumbnail(size, method=method)
        if format is None:
            format = thumb.format

        with io.BytesIO() as output:
            thumb.save(output, format=format, quality=quality)
            raw = output.getvalue()

        if return_info:
            info = {'width': thumb.width, 'height': thumb.height}
            return raw, info
        else:
            return raw

    def __str__(self):
        md5 = hashlib.md5()
        md5.update(self.data)
        return "{0} {1}x{2} {3}".format(self.mime, self.width, self.height,
                                        md5.hexdigest())


class RawProxy(object):
    def __init__(self, parent):
        self.parent = parent

    def resolve(self, norm_key, default=None):
        return self.parent.resolve(norm_key, default, typeless=True)

    def get(self, norm_key, default=None):
        raw_key = norm_key
        norm_key = self.parent._normalize_norm_key(norm_key)
        if norm_key in self.parent.tag_map:
            md_item = self.parent.get(norm_key, default=default, typeless=True)
            return md_item
        else:
            return self.parent.mfile[raw_key]

    def set(self, norm_key, val):
        raw_key = norm_key
        norm_key = self.parent._normalize_norm_key(norm_key)
        if norm_key in self.parent.tag_map:
            self.parent.set(norm_key, val, typeless=True)
        else:
            self.parent.mfile[raw_key] = val

    def __getitem__(self, norm_key):
        return self.get(norm_key, default=None)
    def __setitem__(self, norm_key, val):
        self.set(norm_key, val)


class NotAppendable(Exception):
    pass


class AudioFile(object):
    tag_format = "None"
    mutagen_kls = None

    appendable = True

    # The _DEFAULT_* attributes should not be overridden in subclasses
    _DEFAULT_TAG_ALIASES = {
        'title': 'tracktitle',
        'name': 'tracktitle',
        'disknumber': 'discnumber',
        'totaldisks': 'totaldiscs',
    }

    _DEFAULT_TAG_MAP = {
        'tracktitle': TAG_MAP_ENTRY(type=str),
        'artist': TAG_MAP_ENTRY(type=str),
        'album': TAG_MAP_ENTRY(type=str),
        'albumartist': TAG_MAP_ENTRY(type=str),
        'composer': TAG_MAP_ENTRY(type=str),
        'tracknumber': TAG_MAP_ENTRY(type=int),
        'totaltracks': TAG_MAP_ENTRY(type=int),
        'discnumber': TAG_MAP_ENTRY(type=int),
        'totaldiscs': TAG_MAP_ENTRY(type=int),
        'genre': TAG_MAP_ENTRY(type=str),
        'year': TAG_MAP_ENTRY(type=int, sanitizer=util.sanitize_year),
        'compilation': TAG_MAP_ENTRY(type=bool),
        'lyrics': TAG_MAP_ENTRY(type=str),
        'isrc': TAG_MAP_ENTRY(type=str),
        'comment': TAG_MAP_ENTRY(type=str),

        'artwork': TAG_MAP_ENTRY(type=Artwork),

        '#bitrate': TAG_MAP_ENTRY(getter='bitrate', type=int),
        '#codec': TAG_MAP_ENTRY(getter='codec', type=str),
        '#length': TAG_MAP_ENTRY(getter='length', type=float),
        '#channels': TAG_MAP_ENTRY(getter='channels', type=int),
        '#bitspersample': TAG_MAP_ENTRY(getter='bits_per_sample', type=int),
        '#samplerate': TAG_MAP_ENTRY(getter='sample_rate', type=int),
    }

    _DEFAULT_RESOLVERS = {
        'albumartist': ('albumartist', albumartist_from_comp, 'artist'),
        'artist': ('artist', 'albumartist'),
        'compilation': ('compilation', comp_from_albumartist),
        'discnumber': ('discnumber',
                       lambda afile, norm_key: 1
                       ),
        'totaldiscs': ('totaldiscs',
                       lambda afile, norm_key: afile.get('discnumber', 1)
                       ),
    }

    _DEFAULT_SINGULAR_KEYS = ['tracknumber', 'totaltracks',
                              'discnumber', 'totaldiscs',
                              'year', 'compilation',
                              ]

    # these 3 attributes may be overridden in subclasses
    _TAG_ALIASES = {}
    _TAG_MAP = {}
    _RESOLVERS = {}
    _SINGULAR_KEYS = []


    def __init__(self, filename, _mfile=None):
        self.tag_aliases = self._DEFAULT_TAG_ALIASES.copy()
        self.tag_aliases.update(self._TAG_ALIASES)

        self.tag_map = self._DEFAULT_TAG_MAP.copy()
        self.tag_map.update(self._TAG_MAP)

        self.resolvers = self._DEFAULT_RESOLVERS.copy()
        self.resolvers.update(self._RESOLVERS)

        self.singular_keys = self._DEFAULT_SINGULAR_KEYS.copy()
        self.singular_keys += self._SINGULAR_KEYS

        self.filename = filename
        if _mfile is None:
            self.mfile = mutagen.File(filename)
        else:
            self.mfile = _mfile

        if self.mfile.tags is None:
            self.mfile.add_tags()

    @property
    def raw(self):
        return RawProxy(self)

    def save(self, filename=None, **kwargs):
        """BE CAREFUL, I doubt I did a good job testing tag editing"""
        if filename is None:
            self.mfile.save(**kwargs)
            filename = self.filename
        else:
            shutil.copyfile(self.filename, filename)
            self.mfile.save(filename, **kwargs)

    def _normalize_norm_key(self, norm_key):
        norm_key = norm_key.replace(' ', '').replace('_', '').replace('-', '').lower()
        if self.tag_aliases and norm_key in self.tag_aliases:
            norm_key = self.tag_aliases[norm_key]
        return norm_key

    def resolve(self, norm_key, default=None, typeless=False):
        norm_key = self._normalize_norm_key(norm_key)
        tmap = self.tag_map[norm_key]
        md_type = None if typeless else tmap.type
        md_sanitizer = None if typeless else tmap.sanitizer

        ret = None
        if norm_key in self.resolvers:
            for resolver in self.resolvers[norm_key]:
                if hasattr(resolver, '__call__'):
                    ret = resolver(self, norm_key)
                else:
                    ret = self.get(resolver, default=None, _raw_default=True,
                                   typeless=typeless)
                if ret is not None:
                    break
        else:
            ret = self.get(norm_key, default=None, _raw_default=True,
                           typeless=typeless)

        if not (ret is None or isinstance(ret, MetadataItem)):
            ret = MetadataItem(md_type, md_sanitizer, ret)

        if ret is None:
            ret = MetadataItem(md_type, md_sanitizer, default)

        return ret

    def _ft_getter(self, key):
        return self.mfile.tags.get(key, None)

    def get(self, norm_key, default=None, _raw_default=False, typeless=False):
        norm_key = self._normalize_norm_key(norm_key)
        tmap = self.tag_map[norm_key]
        md_type = None if typeless else tmap.type
        md_sanitizer = None if typeless else tmap.sanitizer

        ret = None
        if hasattr(tmap.getter, '__call__'):
            val = tmap.getter(self, norm_key)
            ret = None if val is None else MetadataItem(md_type, md_sanitizer,
                                                        val)
        elif norm_key.startswith('#'):
            val = getattr(self.mfile.info, tmap.getter)
            if not typeless:
                val = tmap.type(val)
            ret = None if val is None else MetadataItem(md_type, md_sanitizer,
                                                        val)
        elif isinstance(tmap.getter, (list, tuple)):
            val = None
            for getter in tmap.getter:
                if val is not None:
                    break
                if hasattr(getter, '__call__'):
                    val = getter(self, norm_key)
                elif getter in self.mfile.tags:
                    val = self._ft_getter(getter)
            ret = None if val is None else MetadataItem(md_type, md_sanitizer,
                                                        val)
        else:
            try:
                val = self._ft_getter(tmap.getter)
            except KeyError:
                val = None
            ret = None if val is None else MetadataItem(md_type, md_sanitizer,
                                                        val)

        if ret is None:
            if _raw_default:
                ret = default
            else:
                ret = MetadataItem(md_type, md_sanitizer, default)

        return ret

    def _ft_setter(self, key, md_val, appendable=True):
        if self.appendable and appendable:
            self.mfile.tags[key] = md_val.values
        else:
            self.mfile.tags[key] = md_val.value

    def set_raw(self, norm_key, key, md_val, appendable=True):
        if not isinstance(md_val, MetadataItem):
            if isinstance(md_val, (list, tuple)):
                md_val = MetadataItem(type(md_val[0]), None, md_val)
            else:
                md_val = MetadataItem(type(md_val), None, md_val)

        appendable = appendable and norm_key not in self.singular_keys
        if norm_key in self.singular_keys and len(md_val.values) > 1:
            raise ValueError("Key '{0}' can not have multiple values; {1}"
                             "".format(norm_key, md_val.values))

        try:
            self._ft_setter(key, md_val, appendable=appendable)
        except (TypeError, ValueError):
            try:
                v = [str(vi) for vi in md_val.values]
                self._ft_setter(key, MetadataItem(str, None, v),
                                appendable=appendable)
            except Exception:
                success = False
            else:
                success = True
            if not success:
                raise

    def set(self, norm_key, val, typeless=False):
        norm_key = self._normalize_norm_key(norm_key)
        tmap = self.tag_map[norm_key]
        md_type = None if typeless else tmap.type
        md_sanitizer = None if typeless else tmap.sanitizer

        if not isinstance(val, MetadataItem):
            val = MetadataItem(md_type, md_sanitizer, val)

        if hasattr(tmap.setter, '__call__'):
            tmap.setter(self, norm_key, val)
        elif norm_key.startswith('#'):
            raise KeyError("Can not set file info (tags that begin with #)")
        elif isinstance(tmap.setter, (list, tuple)):
            value_set = False
            for setter in tmap.setter:
                if value_set:
                    break
                if hasattr(tmap.setter, '__call__'):
                    tmap.setter(self, norm_key, val)
                    value_set = True
                elif setter in self.mfile.tags:
                    self.set_raw(norm_key, setter, val)
                    value_set = True
            if not value_set:
                self.set_raw(norm_key, tmap.setter[0], val)
        else:
            self.set_raw(norm_key, tmap.setter, val)

    def append_tag(self, norm_key, val):
        norm_key = self._normalize_norm_key(norm_key)
        if not self.appendable:
            raise NotAppendable("{0} can not have multiple values for tags"
                                "".format(self.__class__.__name__))
        if norm_key in self.singular_keys:
            raise NotAppendable("{0} can not have multiple values for '{1}'"
                                "".format(self.__class__.__name__, norm_key))

        existing_val = self.get(norm_key, default=None)
        if existing_val is None:
            new_val = val
        else:
            existing_val.append(val)
            new_val = existing_val
        self.set(norm_key, new_val)

    def append(self, norm_key, val):
        # I'm not sure how i feel about this synonym since append usually
        # takes a single argument in python (i.e. lists etc)
        return self.append_tag(norm_key, val)

    def _ft_rmtag(self, key):
        if key in self.mfile.tags:
            del self.mfile.tags[key]

    def remove_tag(self, norm_key):
        norm_key = self._normalize_norm_key(norm_key)

        if norm_key.startswith('#'):
            raise KeyError("Can not remove tags that start with '#' since "
                           "they are not real tags")

        tmap = self.tag_map[norm_key]

        remover = None
        if tmap.remover:
            remover = tmap.remover

        if not remover:
            if isinstance(tmap.getter, (list, tuple)):
                remover = [g for g in tmap.getter if isinstance(g, util.string_types)]
            if isinstance(tmap.getter, util.string_types):
                remover = [tmap.getter]

        if not remover:
            if isinstance(tmap.setter, (list, tuple)):
                remover = [s for s in tmap.setter if isinstance(s, util.string_types)]
            if isinstance(tmap.setter, util.string_types):
                remover = [tmap.setter]

        if remover is not None:
            if hasattr(remover, '__call__'):
                remover(self, norm_key)
            elif isinstance(remover, (list, tuple)):
                for key in remover:
                    self._ft_rmtag(key)
            elif isinstance(remover, util.string_types):
                self._ft_rmtag(remover)

    def info(self, tags=None, show_empty=False, resolve=False):
        if not tags:
            tags = self._TAG_MAP.keys()
        
        t_lst = []
        for tag in tags:
            if resolve:
                mdi = self.resolve(tag, None)
            else:
                mdi = self.get(tag, None)

            if mdi or show_empty:
                t_lst.append('{0}: {1}'.format(tag, str(mdi)))

        return '\n'.join(t_lst)


    def __getitem__(self, norm_key):
        return self.get(norm_key, default=None)

    def __setitem__(self, norm_key, val):
        self.set(norm_key, val)

    def __contains__(self, key):
        return self[key].values != []

    def __delitem__(self, norm_key):
        self.remove_tag(norm_key)

    def __str__(self):
        return self.info(show_empty=True)

##
## EOF
##
