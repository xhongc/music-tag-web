# coding:UTF-8
import datetime
import os
import time

import music_tag

from applications.task.services.update_ids import save_music


def timestamp_to_dt(timestamp, format_type="%Y-%m-%d %H:%M:%S"):
    # 转换成localtime
    time_local = time.localtime(timestamp)
    # 转换成新的时间格式(2016-05-05 20:28:54)
    dt = time.strftime(format_type, time_local)
    return dt


def folder_update_time(folder_name):
    stat_info = os.stat(folder_name)
    update_time = datetime.datetime.fromtimestamp(stat_info.st_mtime)
    return update_time


def exists_dir(dir_list):
    for _dir in dir_list:
        if os.path.isdir(_dir):
            return True
    return False


def match_song(resource, song_path, select_mode):
    from applications.task.services.music_resource import MusicResource

    file = music_tag.load_file(song_path)
    file_name = song_path.split("/")[-1]
    file_title = file_name.split('.')[0]
    title = file["title"].value or file_title
    artist = file["artist"].value or ""
    album = file["album"].value or ""

    songs = MusicResource(resource).fetch_id3_by_title(title)

    def is_match_artist(my_artist, u_artist):
        if not my_artist or not u_artist:
            return False
        if my_artist == u_artist or my_artist in u_artist or u_artist in my_artist:
            return True

    is_match = False
    song_select = None
    for song in songs:
        if title == song["name"]:
            if select_mode == "simple":
                is_match = True
                song_select = song
                break
            else:
                if is_match_artist(artist, song["artist"]):
                    is_match = True
                    song_select = song
                    break
                elif is_match_artist(album, song["album"]):
                    is_match = True
                    song_select = song
                    break
        elif title in song["name"]:
            if is_match_artist(artist, song["artist"]):
                is_match = True
                song_select = song
                break
            elif is_match_artist(album, song["album"]):
                is_match = True
                song_select = song
                break
        elif song["name"] in title:
            if is_match_artist(artist, song["artist"]):
                is_match = True
                song_select = song
                break
            elif is_match_artist(album, song["album"]):
                is_match = True
                song_select = song
                break
        else:
            continue
    if is_match:
        print(f"{title}>>>{song_select['name']}")
        song_select["filename"] = file_name
        song_select["file_full_path"] = song_path
        song_select["lyrics"] = MusicResource(resource).fetch_lyric(song_select["id"])
        save_music(file, song_select, False)
    return is_match
