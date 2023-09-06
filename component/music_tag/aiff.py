#!/usr/bin/env python
# coding: utf-8

import mutagen.aiff

from component.music_tag.file import TAG_MAP_ENTRY
from component.music_tag.id3 import Id3File


class AiffFile(Id3File):
    tag_format = "AIFF"
    mutagen_kls = mutagen.aiff.AIFF

    def __init__(self, filename, **kwargs):
        super(AiffFile, self).__init__(filename, **kwargs)

        self.tag_map = self.tag_map.copy()
        self.tag_map.update({
            '#codec': TAG_MAP_ENTRY(getter=lambda afile, norm_key: 'aiff',
                                    type=str),
            '#bitspersample': TAG_MAP_ENTRY(getter='sample_size', type=int),
        })
