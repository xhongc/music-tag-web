import datetime
import os
import time
import uuid

from django.conf import settings
from django.db import transaction

from applications.music.models import Folder, Track, Album, Genre, Artist, Attachment
from applications.subsonic.constants import AUDIO_EXTENSIONS_AND_MIMETYPE, COVER_TYPE
from applications.task.services.scan_utils import ScanMusic
from applications.task.utils import folder_update_time, exists_dir
from django_vue_cli.celery_app import app


def get_uuid():
    return str(uuid.uuid4())


@app.task
def full_scan_folder(sub_path=None):
    a = time.time()
    bulk_create = []
    music_folder = os.path.join(settings.MEDIA_ROOT, "music")
    ignore_path = [os.path.join(music_folder, "data")]
    if sub_path:
        stack = sub_path
    else:
        stack = [(None, music_folder)]
    while len(stack) != 0:
        # 从栈里取出数据
        parent_uid, dir_data = stack.pop()
        if os.path.isdir(dir_data):
            if dir_data in ignore_path:
                continue
            try:
                entries = os.scandir(dir_data)
                my_uuid = get_uuid()
            except Exception as e:
                m = f"Error while reading {dir}: {e.__class__.__name__} {e}\n"
                print(m)
                continue
            try:
                sub_path = [(my_uuid, entry.path) for entry in entries]
            except Exception as e:
                m = f"Error2 while reading {dir}: {e.__class__.__name__} {e}\n"
                print(m)
                continue
            finally:
                if hasattr(entries, "close"):
                    entries.close()

            # stack.extend(sub_path)
            if sub_path:
                full_scan_folder.delay(sub_path=sub_path)
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
        if len(bulk_create) % 500 == 0:
            Folder.objects.bulk_create(bulk_create, batch_size=500)
            bulk_create = []
    if len(bulk_create) > 0:
        Folder.objects.bulk_create(bulk_create, batch_size=500)
    print("完成扫描！", time.time() - a)


def update_scan_folder_func(sub_path=None, now_time=None):
    music_folder = os.path.join(settings.MEDIA_ROOT, "music")
    ignore_path = [os.path.join(music_folder, "data")]

    stack = sub_path if sub_path else [(None, music_folder)]
    last_scan_time = Folder.objects.last_scan_time()
    now_time = datetime.datetime.now() if not now_time else now_time
    print(now_time)
    while len(stack) != 0:
        # 从栈里取出数据
        parent_uid, dir_data = stack.pop(0)
        if dir_data in ignore_path:
            continue

        # 文件夹格式
        if os.path.isdir(dir_data):
            try:
                sub_path = os.scandir(dir_data)
            except Exception as e:
                m = f"Error3 while reading {dir}: {e.__class__.__name__} {e}\n"
                print(m)
                continue
            update_time = folder_update_time(dir_data)
            try:
                sub_path_list = [i.path for i in sub_path]
            except Exception as e:
                m = f"Error4 while reading {dir}: {e.__class__.__name__} {e}\n"
                print(m)
                continue
            finally:
                if hasattr(sub_path, "close"):
                    sub_path.close()

            current_folder = Folder.objects.filter(path=dir_data).first()
            if current_folder:
                last_scan_time = current_folder.last_scan_time
                my_uuid = current_folder.uid
                update_data = {
                    "name": dir_data.split("/")[-1],
                    "file_type": "folder",
                    "uid": my_uuid,
                    "parent_id": parent_uid,
                    "updated_at": now_time,
                }
            else:
                my_uuid = get_uuid()
                update_data = {
                    "name": dir_data.split("/")[-1],
                    "file_type": "folder",
                    "uid": my_uuid,
                    "parent_id": parent_uid,
                    "updated_at": now_time,
                }
            Folder.objects.update_or_create(path=dir_data, defaults=update_data)
            if current_folder:
                # 如果文件夹的更新时间小于上次扫描时间and没有子文件夹，就不扫描。
                if update_time < last_scan_time:
                    if not exists_dir(sub_path_list):
                        print("文件夹没有更新，不扫描！", dir_data)
                        Folder.objects.filter(parent_id=current_folder.uid).update(
                            updated_at=now_time
                        )
                        continue

            sub_path_stack = [(my_uuid, i) for i in sub_path_list]
            if sub_path_stack:
                time.sleep(0.1)
                update_scan_folder_func(sub_path_stack, now_time)
        else:
            suffix = dir_data.split(".")[-1]
            if suffix in dict(AUDIO_EXTENSIONS_AND_MIMETYPE):
                my_uuid = get_uuid()
                update_data = {
                    "name": dir_data.split("/")[-1],
                    "file_type": "music",
                    "uid": my_uuid,
                    "parent_id": parent_uid,
                    "updated_at": now_time,
                    "state": "updated"
                }
            elif suffix in COVER_TYPE:
                my_uuid = get_uuid()
                update_data = {
                    "name": dir_data.split("/")[-1],
                    "file_type": "image",
                    "uid": my_uuid,
                    "parent_id": parent_uid,
                    "updated_at": now_time,
                    "state": "updated"
                }
            else:
                continue
            Folder.objects.update_or_create(path=dir_data, defaults=update_data)


@app.task
def update_scan_folder(sub_path=None, now_time=None):
    now_time = datetime.datetime.now() if not now_time else now_time
    update_scan_folder_func(sub_path, now_time)
    folder_lst = Folder.objects.filter(updated_at=now_time, file_type="folder")
    for folder in folder_lst:
        # 没有扫描到的子文件夹
        path_list = list(
            Folder.objects.filter(parent_id=folder.uid, file_type="music").exclude(updated_at=now_time).values_list(
                "path", flat=True))
        with transaction.atomic():
            if path_list:
                Track.objects.filter(path__in=path_list).delete()
            print(Folder.objects.filter(parent_id=folder.uid).exclude(updated_at=now_time).values("path"))
            Folder.objects.filter(parent_id=folder.uid).exclude(updated_at=now_time).delete()
    print("完成更新扫描！")


@app.task
def scan_folder():
    if Folder.objects.count() > 0:
        update_scan_folder()
    else:
        full_scan_folder()


@app.task
def scan_music_id3():
    a = time.time()
    ScanMusic("/").scan()
    print(time.time() - a)


@app.task
def scan():
    if Folder.objects.count() > 0:
        update_scan_folder()
    else:
        full_scan_folder()
    ScanMusic("/").scan()


def clear_music():
    Folder.objects.all().delete()
    Track.objects.all().delete()
    Album.objects.all().delete()
    Genre.objects.all().delete()
    Artist.objects.all().delete()
    Attachment.objects.all().delete()
