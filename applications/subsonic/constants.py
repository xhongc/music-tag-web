AUDIO_EXTENSIONS_AND_MIMETYPE = [
    # keep the most correct mimetype for each extension at the bottom
    ("mp3", "audio/mp3"),
    ("mp3", "audio/mpeg3"),
    ("mp3", "audio/x-mp3"),
    ("mp3", "audio/mpeg"),
    ("ogg", "video/ogg"),
    ("ogg", "audio/ogg"),
    ("opus", "audio/opus"),
    ("aac", "audio/x-m4a"),
    ("m4a", "audio/x-m4a"),
    ("flac", "audio/x-flac"),
    ("flac", "audio/flac"),
    ("aif", "audio/aiff"),
    ("aif", "audio/x-aiff"),
    ("aiff", "audio/aiff"),
    ("aiff", "audio/x-aiff"),
]
COVER_TYPE = {"jpg", "jpeg", "png"}
EXTENSION_TO_MIMETYPE = {ext: mt for ext, mt in AUDIO_EXTENSIONS_AND_MIMETYPE}
