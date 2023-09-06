#!/usr/bin/env python
# coding: utf-8

import mutagen.smf

from component.music_tag.file import AudioFile


# smf: standard midi file


class SmfFile(AudioFile):
    tag_format = "SMF"
    mutagen_kls = mutagen.smf.SMF

    def __init__(self, filename, **kwargs):
        raise NotImplementedError("SMF format not implemented")
