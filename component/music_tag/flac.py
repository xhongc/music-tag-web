#!/usr/bin/env python
# coding: utf-8

import base64

import mutagen.flac

from component.music_tag import util
from component.music_tag.file import Artwork, AudioFile, MetadataItem, TAG_MAP_ENTRY


def get_pictures(afile, norm_key):
    artworks = [Artwork(p.data, width=p.width, height=p.height,
                        fmt=p.mime.split('/')[-1], pic_type=p.type)
                for p in afile.mfile.pictures]
    return MetadataItem(Artwork, None, artworks)


def set_pictures(afile, norm_key, artworks):
    if not isinstance(artworks, MetadataItem):
        raise TypeError()

    afile.mfile.clear_pictures()
    for i, art in enumerate(artworks.values):
        if any(v is None for v in (art.mime, art.width, art.height, art.depth)):
            raise ImportError("Please install Pillow to properly handle images")
        pic = mutagen.flac.Picture()
        pic.data = art.raw
        pic.type = art.pic_type
        pic.mime = art.mime
        pic.width = art.width
        pic.height = art.height
        pic.depth = art.depth
        afile.mfile.add_picture(pic)


def rm_pictures(afile, norm_key):
    afile.mfile.clear_pictures()


class FlacFile(AudioFile):
    tag_format = "FLAC"
    mutagen_kls = mutagen.flac.FLAC

    _TAG_MAP = {
        'tracktitle': TAG_MAP_ENTRY(getter='title', setter='title', type=str),
        'artist': TAG_MAP_ENTRY(getter='artist', setter='artist', type=str),
        'album': TAG_MAP_ENTRY(getter='album', setter='album', type=str),
        'albumartist': TAG_MAP_ENTRY(getter='albumartist', setter='albumartist',
                                     type=str),
        'composer': TAG_MAP_ENTRY(getter='composer', setter='composer', type=str),
        'tracknumber': TAG_MAP_ENTRY(getter='tracknumber', setter='tracknumber',
                                     type=int),
        'totaltracks': TAG_MAP_ENTRY(getter='tracktotal', setter='tracktotal',
                                     type=int),
        'discnumber': TAG_MAP_ENTRY(getter='discnumber', setter='discnumber',
                                    type=int),
        'totaldiscs': TAG_MAP_ENTRY(getter='disctotal', setter='disctotal',
                                    type=int),
        'genre': TAG_MAP_ENTRY(getter='genre', setter='genre', type=str),
        'year': TAG_MAP_ENTRY(getter=('date', 'originaldate'),
                              setter=('date', 'originaldate'),
                              type=int, sanitizer=util.sanitize_year),
        'lyrics': TAG_MAP_ENTRY(getter='lyrics', setter='lyrics', type=str),
        'isrc': TAG_MAP_ENTRY(getter='isrc', setter='isrc', type=str),
        'comment': TAG_MAP_ENTRY(getter='comment', setter='comment', type=str),
        'compilation': TAG_MAP_ENTRY(getter='compilation', setter='compilation',
                                     type=int, sanitizer=util.sanitize_bool),

        'artwork': TAG_MAP_ENTRY(getter=get_pictures, setter=set_pictures,
                                 remover=rm_pictures,
                                 type=Artwork),

        '#codec': TAG_MAP_ENTRY(getter=lambda afile, norm_key: 'flac',
                                type=str),
    }

    def _ft_setter(self, key, md_val, appendable=True):
        if self.appendable and appendable:
            self.mfile.tags[key] = [str(v) for v in md_val.values]
        else:
            self.mfile.tags[key] = str(md_val.value)
