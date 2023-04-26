import music_tag
from django.conf import settings

from applications.music.models import Folder, Track
from applications.subsonic.constants import AUDIO_EXTENSIONS_AND_MIMETYPE, COVER_TYPE
from django_vue_cli.celery_app import app
import os
import uuid


def get_uuid():
    return str(uuid.uuid4())


@app.task
def full_scan():
    music_folder = os.path.join(settings.MEDIA_ROOT, "music")
    bulk_create = []
    stack = [(None, music_folder)]
    while len(stack) != 0:
        # 从栈里取出数据
        parent_uid, dir_data = stack.pop(0)
        if os.path.isdir(dir_data):
            sub_path = os.listdir(dir_data)
            my_uuid = get_uuid()
            sub_path = [(my_uuid, f"{dir_data}/{i}") for i in sub_path]
            stack.extend(sub_path)
            bulk_create.append(
                Folder(**{
                    "name": dir_data.split("/")[-1],
                    "path": dir_data,
                    "file_type": "folder",
                    "uid": my_uuid,
                    "parent_id": parent_uid
                })
            )
        else:
            suffix = dir_data.split(".")[-1]
            if suffix in dict(AUDIO_EXTENSIONS_AND_MIMETYPE):
                print(dir_data)
                my_uuid = get_uuid()
                bulk_create.append(
                    Folder(**{
                        "name": dir_data.split("/")[-1],
                        "path": dir_data,
                        "file_type": "music",
                        "uid": my_uuid,
                        "parent_id": parent_uid
                    })
                )
            elif suffix in COVER_TYPE:
                my_uuid = get_uuid()
                bulk_create.append(
                    Folder(**{
                        "name": dir_data.split("/")[-1],
                        "path": dir_data,
                        "file_type": "image",
                        "uid": my_uuid,
                        "parent_id": parent_uid
                    })
                )
    Folder.objects.bulk_create(bulk_create, batch_size=500)


@app.task
def scan_music_id3():
    music_list = Folder.objects.filter(file_type="music").all()
    bulk_create = []
    for music in music_list:
        f = music_tag.load_file(music.path)
        Track.objects.filter()