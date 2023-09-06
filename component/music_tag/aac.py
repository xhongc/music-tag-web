#!/usr/bin/env python
# coding: utf-8

import mutagen.aac

from component.music_tag.file import TAG_MAP_ENTRY
from component.music_tag.apev2 import Apev2File


class AacFile(Apev2File):
    tag_format = "AAC"
    mutagen_kls = mutagen.aac.AAC

    _TAG_MAP = Apev2File._TAG_MAP.copy()
    _TAG_MAP.update({
    })
