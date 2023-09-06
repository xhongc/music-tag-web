#!/usr/bin/env python
# coding: utf-8

import base64
import itertools

import mutagen.ogg
import mutagen.oggvorbis
import mutagen.oggopus
import mutagen.oggflac
import mutagen.oggtheora
import mutagen.oggspeex

from component.music_tag import util
from component.music_tag.file import Artwork, AudioFile, MetadataItem, TAG_MAP_ENTRY


def get_pictures(afile, norm_key):
    artworks = []

    pics_dat = afile.mfile.get("coverart", [])
    mimes = afile.mfile.get("coverartmime", [])
    for dat, mime in itertools.zip_longest(pics_dat, mimes, fillvalue=""):
        image_data = base64.b64decode(dat.encode("ascii"))
        artworks = Artwork(image_data)

    for p in afile.mfile.tags['metadata_block_picture']:
        pb = util.parse_picture_block(base64.standard_b64decode(p))
        art = Artwork(pb.data, width=pb.width, height=pb.height, fmt=pb.format)
        artworks.append(art)

    return MetadataItem(Artwork, None, artworks)

def set_pictures(afile, norm_key, artworks):
    if not isinstance(artworks, MetadataItem):
        raise TypeError()

    pics = []
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

        pic_data = base64.b64encode(pic.write()).decode('ascii')
        pics.append(pic_data)
    afile.mfile.tags['metadata_block_picture'] = pics

def rm_pictures(afile, norm_key):
    for k in ('coverart', 'coverartmime', 'metadata_block_picture'):
        if k in afile.mfile.tags:
            del afile.mfile.tags[k]


class OggFile(AudioFile):
    tag_format = "Ogg"
    mutagen_kls = mutagen.ogg.OggFileType

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
    }

    def _ft_setter(self, key, md_val, appendable=True):
        if self.appendable and appendable:
            self.mfile.tags[key] = [str(v) for v in md_val.values]
        else:
            self.mfile.tags[key] = str(md_val.value)


class OggFlacFile(OggFile):
    tag_format = "OggFlac"
    mutagen_kls = mutagen.oggflac.OggFLAC


class OggSpeexFile(OggFile):
    tag_format = "OggSpeex"
    mutagen_kls = mutagen.oggspeex.OggSpeex


class OggTheoraFile(OggFile):
    tag_format = "OggTheora"
    mutagen_kls = mutagen.oggtheora.OggTheora


class OggVorbisFile(OggFile):
    tag_format = "OggVorbis"
    mutagen_kls = mutagen.oggvorbis.OggVorbis

    _TAG_MAP = OggFile._TAG_MAP.copy()
    _TAG_MAP.update({
        '#codec': TAG_MAP_ENTRY(getter=lambda afile, norm_key: 'Ogg Vorbis',
                                type=str),
        '#bitspersample': TAG_MAP_ENTRY(getter=lambda afile, norm_key: None,
                                type=int),
    })


class OggOpusFile(OggFile):
    tag_format = "OggOpus"
    mutagen_kls = mutagen.oggopus.OggOpus

    _TAG_MAP = OggFile._TAG_MAP.copy()
    _TAG_MAP.update({
        '#codec': TAG_MAP_ENTRY(getter=lambda afile, norm_key: 'Ogg Opus',
                                type=str),
        '#bitspersample': TAG_MAP_ENTRY(getter=lambda afile, norm_key: None,
                                type=int),
        '#samplerate': TAG_MAP_ENTRY(getter=lambda afile, norm_key: None,
                                     type=int),
        '#bitrate': TAG_MAP_ENTRY(getter=lambda afile, norm_key: None,
                                  type=int),
    })
