# coding:UTF-8
import datetime
import os
import re
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


def match_score(my_value, u_value):
    try:
        my_value = my_value.lower().replace(" ", "")
        u_value = u_value.lower().replace(" ", "")
        if not my_value or not u_value:
            return 0
        if my_value == u_value:
            return 2
        elif my_value in u_value or u_value in my_value:
            return 1
        return 0
    except Exception:
        return 0


def match_song(resource, song_path, select_mode):
    from applications.task.services.music_resource import MusicResource

    file = music_tag.load_file(song_path)
    file_name = song_path.split("/")[-1]
    file_title = file_name.split('.')[0]
    title = file["title"].value or file_title
    artist = file["artist"].value or ""
    album = file["album"].value or ""

    songs = MusicResource(resource).fetch_id3_by_title(title)

    is_match = False
    song_select = None
    match_score_map = {
        "title": 0,
        "artist": 0,
        "album": 0,
    }
    for song in songs:
        match_score_map["title"] = match_score(title, song["name"])
        match_score_map["artist"] = match_score(artist if artist else title, song["artist"])
        match_score_map["album"] = match_score(album if album else title, song["album"])
        if sum(match_score_map.values()) >= 3:
            is_match = True
            song_select = song
            break
        if select_mode == "simple":
            if match_score_map["title"] == 2:
                is_match = True
                song_select = song
                break
    if is_match:
        print(f"{title}>>>{song_select['name']}::{match_score_map}")
        song_select["filename"] = file_name
        song_select["file_full_path"] = song_path
        song_select["lyrics"] = MusicResource(resource).fetch_lyric(song_select["id"])
        save_music(file, song_select, False)
    return is_match


def detect_language(lyrics):
    chinese_pattern = re.compile(r'[\u4e00-\u9fa5]')
    english_pattern = re.compile(r'[a-zA-Z]')
    japanese_pattern = re.compile(r'[\u0800-\u4e00]')
    korean_pattern = re.compile(r'[\uac00-\ud7a3]')
    thai_pattern = re.compile(r'[\u0e00-\u0e7f]')

    chinese_count = len(re.findall(chinese_pattern, lyrics))
    english_count = len(re.findall(english_pattern, lyrics))
    japanese_count = len(re.findall(japanese_pattern, lyrics))
    korean_count = len(re.findall(korean_pattern, lyrics))
    thai_count = len(re.findall(thai_pattern, lyrics))
    if chinese_count > english_count and chinese_count > japanese_count and chinese_count > korean_count \
            and chinese_count > thai_count:
        return '中文'
    elif english_count > chinese_count and english_count > japanese_count and english_count > korean_count \
            and english_count > thai_count:
        return '英文'
    elif japanese_count > chinese_count and japanese_count > english_count and japanese_count > korean_count \
            and japanese_count > thai_count:
        return '日文'
    elif korean_count > chinese_count and korean_count > english_count and korean_count > japanese_count \
            and korean_count > thai_count:
        return '韩文'
    elif thai_count > chinese_count and thai_count > english_count and thai_count > japanese_count \
            and thai_count > korean_count:
        return '泰文'
    else:
        return '未知'
