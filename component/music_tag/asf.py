#!/usr/bin/env python
# coding: utf-8

# asf is a microsoft format (wma, wmv, etc.)

import mutagen.asf
from mutagen.id3 import PictureType

from component.music_tag import util

from component.music_tag.file import AudioFile, TAG_MAP_ENTRY, Artwork, MetadataItem

pic_type2tag = {
    PictureType.COVER_FRONT: 'Cover Art (Front)',
    PictureType.COVER_BACK: 'Cover Art (Back)',
}
pic_tag2type = {}
for key, val in pic_type2tag.items():
    pic_tag2type[val] = key
del key, val


def get_pictures(afile, norm_key):
    artworks = []
    if "WM/Picture" in afile.mfile.tags:
        p = afile.mfile.tags["WM/Picture"][0].value
        if not isinstance(p, bytes):
            p = eval(p)
        try:
            artwork = Artwork(p)
        except OSError:
            artwork = Artwork(p.split(b'\0', 1)[1])
        artworks.append(artwork)
    return MetadataItem(Artwork, None, artworks)


def set_pictures(afile, norm_key, artworks):
    for art in artworks.values:
        pic_tag = "WM/Picture"
        raw = (pic_tag + '.jpg').encode('ascii') + b'\0' + art.raw
        afile.mfile.tags[pic_tag] = raw


class AsfFile(AudioFile):
    tag_format = "ASF"
    mutagen_kls = mutagen.asf.ASF
    _TAG_MAP = {
        'tracktitle': TAG_MAP_ENTRY(getter='Title', setter='Title', type=str),
        'artist': TAG_MAP_ENTRY(getter='Author', setter='Author', type=str),
        'album': TAG_MAP_ENTRY(getter='WM/AlbumTitle', setter='WM/AlbumTitle', type=str),
        'albumartist': TAG_MAP_ENTRY(getter='albumartist', setter='albumartist',
                                     type=str),
        'composer': TAG_MAP_ENTRY(getter='composer', setter='composer', type=str),
        'tracknumber': TAG_MAP_ENTRY(getter='WM/TrackNumber', setter='WM/TrackNumber',
                                     type=str),
        'totaltracks': TAG_MAP_ENTRY(getter='tracktotal', setter='tracktotal',
                                     type=int),
        'discnumber': TAG_MAP_ENTRY(getter='discnumber', setter='discnumber',
                                    type=int),
        'totaldiscs': TAG_MAP_ENTRY(getter='disctotal', setter='disctotal',
                                    type=int),
        'genre': TAG_MAP_ENTRY(getter='WM/Genre', setter='WM/Genre', type=str),
        'year': TAG_MAP_ENTRY(getter=('TDOR', 'originaldate'),
                              setter=('TDOR', 'originaldate'),
                              type=int, sanitizer=util.sanitize_year),
        'lyrics': TAG_MAP_ENTRY(getter='lyrics-eng', setter='lyrics-eng', type=str),
        'isrc': TAG_MAP_ENTRY(getter='isrc', setter='isrc', type=str),
        'comment': TAG_MAP_ENTRY(getter='Description', setter='Description', type=str),
        'compilation': TAG_MAP_ENTRY(getter='compilation', setter='compilation',
                                     type=int, sanitizer=util.sanitize_bool),
        'artwork': TAG_MAP_ENTRY(getter=get_pictures, setter=set_pictures,
                                 remover=list(pic_tag2type.keys()),
                                 type=Artwork),
        '#codec': TAG_MAP_ENTRY(getter=lambda afile, norm_key: 'flac',
                                type=str),
    }

    def __init__(self, filename, **kwargs):
        super(AsfFile, self).__init__(filename, **kwargs)
