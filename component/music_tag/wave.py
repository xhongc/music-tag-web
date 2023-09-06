#!/usr/bin/env python
# coding: utf-8

try:
    import mutagen.wave

    from component.music_tag.id3 import Id3File


    class WaveId3File(Id3File):
        tag_format = "Wave[Id3]"
        mutagen_kls = mutagen.wave.WAVE

        def __init__(self, filename, **kwargs):
            super(WaveId3File, self).__init__(filename, **kwargs)

            # self.tag_map = self.tag_map.copy()
            # self.tag_map.update({
            #     '#codec': TAG_MAP_ENTRY(getter=lambda afile, norm_key: 'mp3',
            #                             type=str),
            #     '#bitspersample': TAG_MAP_ENTRY(getter=lambda afile, norm_key: None,
            #                             type=int),
            # })
            
except ImportError:
    pass
