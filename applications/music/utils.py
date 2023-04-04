from django.db import transaction

from applications.music.models import Music

def create_music(filename):
    bulk_list = []
    with transaction.atomic():
        with open(f"/Users/macbookair/coding/demo/music/{filename}.txt", "r") as f:
            song_list = f.readlines()
            for song in song_list:
                category, fs_id, isdir, local_ctime, local_mtime, path, server_ctime, server_mtime, server_filename, size = song.split(
                    "||")
                parent_path = path.split("/")[-2]
                bulk_list.append(Music(**{
                    "title": server_filename,
                    "fs_id": fs_id,
                    "path": path,
                    "parent_path": parent_path,
                    "size": size
                }))
        Music.objects.bulk_create(bulk_list)
