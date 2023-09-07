import datetime
import os
import shutil
import time
import uuid
from collections import defaultdict

from component import music_tag
from django.conf import settings
from django.db import transaction

from applications.music.models import Folder, Track, Album, Genre, Artist, Attachment
from applications.subsonic.constants import AUDIO_EXTENSIONS_AND_MIMETYPE, COVER_TYPE
from applications.task.constants import ALLOW_TYPE
from applications.task.models import TaskRecord, Task
from applications.task.services.music_ids import MusicIDS
from applications.task.services.music_resource import MusicResource
from applications.task.services.scan_utils import ScanMusic, MusicInfo
from applications.task.utils import folder_update_time, exists_dir, match_song
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


@app.task
def update_scan_folder(sub_path=None):
    music_folder = os.path.join(settings.MEDIA_ROOT, "music")
    ignore_path = [os.path.join(music_folder, "data")]
    print(music_folder)
    if sub_path:
        stack = sub_path
    else:
        stack = [(None, music_folder)]
    last_folder = Folder.objects.order_by("-last_scan_time").first()
    if last_folder:
        last_scan_time = last_folder.last_scan_time
    else:
        last_scan_time = datetime.datetime(1970, 1, 1)
    now_time = datetime.datetime.now()
    while len(stack) != 0:
        # 从栈里取出数据
        parent_uid, dir_data = stack.pop(0)
        if dir_data in ignore_path:
            continue
        if os.path.isdir(dir_data):
            try:
                sub_path = os.scandir(dir_data)
            except Exception as e:
                m = f"Error3 while reading {dir}: {e.__class__.__name__} {e}\n"
                print(m)
                continue
            update_time = folder_update_time(dir_data)
            if update_time < last_scan_time:
                try:
                    sub_path_list = [i.path for i in sub_path]
                except Exception as e:
                    m = f"Error4 while reading {dir}: {e.__class__.__name__} {e}\n"
                    print(m)
                    continue
                finally:
                    if hasattr(sub_path, "close"):
                        sub_path.close()
                if not exists_dir(sub_path_list):
                    continue
            current_folder = Folder.objects.filter(path=dir_data).first()
            if current_folder:
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
            try:
                sub_path = [(my_uuid, f"{dir_data}/{i}") for i in sub_path]
            except Exception as e:
                m = f"Error5 while reading {dir}: {e.__class__.__name__} {e}\n"
                print(m)
                continue
            finally:
                if hasattr(sub_path, "close"):
                    sub_path.close()
            # stack.extend(sub_path)
            if sub_path:
                update_scan_folder.delay(sub_path)
        else:
            suffix = dir_data.split(".")[-1]
            if suffix in dict(AUDIO_EXTENSIONS_AND_MIMETYPE):
                print(dir_data)
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
    folder_lst = Folder.objects.filter(updated_at=now_time, file_type="folder")
    for folder in folder_lst:
        path_list = list(
            Folder.objects.filter(parent_id=folder.uid).exclude(updated_at=now_time).values_list("path", flat=True))
        with transaction.atomic():
            Track.objects.filter(path__in=path_list).delete()
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


def batch_auto_tag_task(batch, source_list, select_mode):
    """
    自动刮削任务
    source_list: ["migu", "qmusic", "netease"]
    """
    folder_list = TaskRecord.objects.filter(batch=batch, icon="icon-folder").all()
    for folder in folder_list:
        data = os.scandir(folder.full_path)
        bulk_set = []
        for entry in data:
            each = entry.name
            file_type = each.split(".")[-1]
            file_name = ".".join(each.split(".")[:-1])
            if file_type not in ALLOW_TYPE:
                continue
            bulk_set.append(TaskRecord(**{
                "batch": batch,
                "song_name": file_name,
                "full_path": f"{folder.full_path}/{each}",
                "icon": "icon-music",

            }))
        TaskRecord.objects.bulk_create(bulk_set)
    task_list = TaskRecord.objects.filter(batch=batch).exclude(icon="icon-folder").all()
    for task in task_list:
        is_match = False
        for resource in source_list:
            print("开始匹配", resource)
            try:
                is_match = match_song(resource, task.full_path, select_mode)
            except Exception as e:
                print(e)
                is_match = False
                break
            if is_match:
                task.state = "success"
                task.save()
                parent_path = os.path.dirname(task.full_path)
                Task.objects.update_or_create(full_path=task.full_path, defaults={
                    "state": task.state,
                    "parent_path": parent_path,
                    "filename": os.path.basename(task.full_path),
                    "song_name": task.song_name,
                    "artist_name": task.artist_name,
                })
                break
        if not is_match:
            task.state = "failed"
            task.save()
            parent_path = os.path.dirname(task.full_path)
            Task.objects.update_or_create(full_path=task.full_path, defaults={
                "state": task.state,
                "parent_path": parent_path,
                "filename": os.path.basename(task.full_path),
                "song_name": task.song_name,
                "artist_name": task.artist_name,
            })


def tidy_folder_task(music_path_list, tidy_config):
    """整理文件夹任务"""
    root_path = tidy_config.get("root_path")
    first_dir = tidy_config.get("first_dir")
    second_dir = tidy_config.get("second_dir")

    if second_dir:
        tidy_map = defaultdict(lambda: defaultdict(list))
        for music_path in music_path_list:
            file = MusicIDS(music_path)
            first_value = getattr(file, first_dir, "未知")
            second_value = getattr(file, second_dir, "未知")
            tidy_map[first_value][second_value].append(music_path)
        for first_value, second_map in tidy_map.items():
            first_path = os.path.join(root_path, first_value)
            if not os.path.exists(first_path):
                os.makedirs(first_path)
            for second_value, music_path_list in second_map.items():
                second_path = os.path.join(first_path, second_value)
                if not os.path.exists(second_path):
                    os.makedirs(second_path)
                for music_path in music_path_list:
                    shutil.move(music_path, second_path)
    else:
        tidy_map = defaultdict(list)
        for music_path in music_path_list:
            file = MusicIDS(music_path)
            first_value = getattr(file, first_dir, "未知")
            tidy_map[first_value].append(music_path)
        for first_value, music_path_list in tidy_map.items():
            first_path = os.path.join(root_path, first_value)
            if not os.path.exists(first_path):
                os.makedirs(first_path)
            for music_path in music_path_list:
                shutil.move(music_path, first_path)
