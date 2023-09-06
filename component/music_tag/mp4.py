#!/usr/bin/env python
# coding: utf-8

# FIXME: does artwork need a proper shim?

import mutagen.mp4
import mutagen.easymp4
from mutagen.mp4 import MP4FreeForm

from component.music_tag import util
from component.music_tag.file import Artwork, AudioFile, MetadataItem, TAG_MAP_ENTRY


mutagen.easymp4.EasyMP4Tags.RegisterTextKey("compilation", "cpil")


_MP4_ISRC_KEY = '----:com.apple.iTunes:ISRC'


def get_tracknum(afile, norm_key):
    trkn = afile.mfile.get('trkn', [(None, None)])[0]
    try:
        return trkn[0]
    except IndexError:
        return None

def set_tracknum(afile, norm_key, val):
    trkn = list(afile.mfile.tags.get('trkn', [(0, 0)])[0])
    trkn += [0] * (2 - len(trkn))
    trkn[0] = int(val)
    trkn = tuple([0 if i is None else int(i) for i in trkn])
    afile.mfile.tags['trkn'] = [trkn]

def get_totaltracks(afile, norm_key):
    trkn = afile.mfile.get('trkn', [(None, None)])[0]
    try:
        return trkn[1]
    except IndexError:
        return None

def set_totaltracks(afile, norm_key, val):
    trkn = list(afile.mfile.tags.get('trkn', [(0, 0)])[0])
    trkn += [0] * (2 - len(trkn))
    trkn[1] = int(val)
    trkn = tuple([0 if i is None else int(i) for i in trkn])
    afile.mfile.tags['trkn'] = [trkn]

def get_discnum(afile, norm_key):
    trkn = afile.mfile.get('disk', [(None, None)])[0]
    try:
        return trkn[0]
    except IndexError:
        return None

def set_discnum(afile, norm_key, val):
    disc = list(afile.mfile.tags.get('disk', [(0, 0)])[0])
    disc += [0] * (2 - len(disc))
    disc[0] = int(val)
    disc = [0 if i is None else i for i in disc]
    afile.mfile.tags['disk'] = [tuple(disc)]

def get_totaldiscs(afile, norm_key):
    trkn = afile.mfile.get('disk', [(None, None)])[0]
    try:
        return trkn[1]
    except IndexError:
        return None

def set_totaldiscs(afile, norm_key, val):
    disc = list(afile.mfile.tags.get('disk', [(0, 0)])[0])
    disc += [0] * (2 - len(disc))
    disc[1] = int(val)
    disc = [0 if i is None else i for i in disc]
    afile.mfile.tags['disk'] = [tuple(disc)]

def get_artwork(afile, norm_key):
    fmt_lut = {mutagen.mp4.MP4Cover.FORMAT_JPEG: 'jpeg',
               mutagen.mp4.MP4Cover.FORMAT_PNG: 'png',
              }
    artworks = [Artwork(bytes(p)) for p in afile.mfile.tags['covr']]

    return MetadataItem(Artwork, None, artworks)

def set_artwork(afile, norm_key, artworks):
    if not isinstance(artworks, MetadataItem):
        raise TypeError()

    pics = []
    for art in artworks.values:
        if any(v is None for v in (art.mime, )):
            raise ImportError("Please install Pillow to properly handle images")

        mime_fmt = art.mime.split('/')[1].upper()
        if mime_fmt == 'JPEG':
            img_fmt = mutagen.mp4.MP4Cover.FORMAT_JPEG
        elif mime_fmt == 'PNG':
            img_fmt = mutagen.mp4.MP4Cover.FORMAT_PNG
        else:
            raise TypeError('mp4 artwork should be either jpeg or png')

        pics.append(mutagen.mp4.MP4Cover(art.raw, imageformat=img_fmt))
    afile.mfile.tags['covr'] = pics

def freeform_get(afile, norm_key):
    return [val.decode() for val in afile.mfile.get(norm_key, [])]
    
def freeform_set(afile, norm_key, val):
    ff_vals = [MP4FreeForm(v.encode('utf-8')) for v in val.values]
    afile.mfile.tags[norm_key] = ff_vals
    

class Mp4File(AudioFile):
    tag_format = "mp4"
    mutagen_kls = mutagen.mp4.MP4

    _TAG_MAP = {
        'tracktitle': TAG_MAP_ENTRY(getter='©nam', setter='©nam', type=str),
        'artist': TAG_MAP_ENTRY(getter='©ART', setter='©ART', type=str),
        'album': TAG_MAP_ENTRY(getter='©alb', setter='©alb', type=str),
        'albumartist': TAG_MAP_ENTRY(getter='aART', setter='aART', type=str),
        'composer': TAG_MAP_ENTRY(getter='©wrt', setter='©wrt', type=str),
        'tracknumber': TAG_MAP_ENTRY(getter=get_tracknum,
                                     setter=set_tracknum,
                                     type=int),
        'totaltracks': TAG_MAP_ENTRY(getter=get_totaltracks,
                                     setter=set_totaltracks,
                                     type=int),
        'discnumber': TAG_MAP_ENTRY(getter=get_discnum,
                                    setter=set_discnum,
                                    type=int),
        'totaldiscs': TAG_MAP_ENTRY(getter=get_totaldiscs,
                                    setter=set_totaldiscs,
                                    type=int),
        'genre': TAG_MAP_ENTRY(getter='©gen', setter='©gen', type=str),
        'year': TAG_MAP_ENTRY(getter='©day', setter='©day', type=int,
                              sanitizer=util.sanitize_year),
        'lyrics': TAG_MAP_ENTRY(getter='©lyr', setter='©lyr', type=str),
        'isrc': TAG_MAP_ENTRY(getter=lambda f, k: freeform_get(f, _MP4_ISRC_KEY),
                              setter=lambda f, k, v: freeform_set(f, _MP4_ISRC_KEY, v),
                              remover=_MP4_ISRC_KEY,
                              type=str),
        'comment': TAG_MAP_ENTRY(getter='©cmt', setter='©cmt', type=str),
        'compilation': TAG_MAP_ENTRY(getter='cpil', setter='cpil', type=bool,
                                     sanitizer=util.sanitize_bool),

        'artwork': TAG_MAP_ENTRY(getter=get_artwork, setter=set_artwork,
                                 type=Artwork),
    }


class EasyMp4File(Mp4File):
    tag_format = "mp4"
    mutagen_kls = mutagen.easymp4.EasyMP4

    _TAG_MAP = Mp4File._TAG_MAP.copy()
    _TAG_MAP.update({
        'tracktitle': TAG_MAP_ENTRY(getter='title', setter='title', type=str),
        'artist': TAG_MAP_ENTRY(getter='artist', setter='artist', type=str),
        'album': TAG_MAP_ENTRY(getter='album', setter='album', type=str),
        'albumartist': TAG_MAP_ENTRY(getter='albumartist', setter='albumartist', type=str),
        'tracknumber': TAG_MAP_ENTRY(getter=util.get_easy_tracknum,
                                     setter=util.set_easy_tracknum,
                                     type=int),
        'totaltracks': TAG_MAP_ENTRY(getter=util.get_easy_totaltracks,
                                     setter=util.set_easy_totaltracks,
                                     type=int),
        'discnumber': TAG_MAP_ENTRY(getter=util.get_easy_discnum,
                                    setter=util.set_easy_discnum,
                                    type=int),
        'totaldiscs': TAG_MAP_ENTRY(getter=util.get_easy_totaldiscs,
                                    setter=util.set_easy_totaldiscs,
                                    type=int),
        'genre': TAG_MAP_ENTRY(getter='genre', setter='genre', type=str),
        'year': TAG_MAP_ENTRY(getter='date', setter='date', type=int,
                              sanitizer=util.sanitize_year),
        'compilation': TAG_MAP_ENTRY(getter='compilation', setter='compilation',
                                     type=bool),

        'artwork': TAG_MAP_ENTRY(getter='covr', type=Artwork),
    })
