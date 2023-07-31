import os

import music_tag

from applications.task.models import Task
from applications.utils.constant_template import ConstantTemplate
from applications.utils.send import send

COPYRIGHT = "感谢您的聆听，music-tag-web打上标签。POW~"


def update_music_info(music_id3_info, is_raw_thumbnail=False):
    for each in music_id3_info:
        f = music_tag.load_file(each["file_full_path"])
        save_music(f, each, is_raw_thumbnail)
        parent_path = os.path.dirname(each["file_full_path"])
        filename = os.path.basename(each["file_full_path"])
        Task.objects.update_or_create(full_path=each["file_full_path"], defaults={
            "state": "success",
            "parent_path": parent_path,
            "filename": filename
        })


def save_music(f, each, is_raw_thumbnail):
    base_filename = ".".join(os.path.basename(f.filename).split(".")[:-1])
    file_ext = os.path.basename(f.filename).split(".")[-1]
    var_dict = {
        "title": f["title"].value,
        "artist": f["artist"].value,
        "albumartist": f["albumartist"].value,
        "discnumber": f["discnumber"].value,
        "tracknumber": f["tracknumber"].value,
        "album": f["album"].value,
        "filename": base_filename
    }
    if each.get("title", None):
        if "${" in each["title"]:
            f["title"] = ConstantTemplate(each["title"]).resolve_data(var_dict)
        else:
            f["title"] = each["title"]
    if each.get("artist", None):
        if "${" in each["artist"]:
            f["artist"] = ConstantTemplate(each["artist"]).resolve_data(var_dict)
        else:
            f["artist"] = each["artist"]
    if each.get("album", None):
        if "${" in each["album"]:
            f["album"] = ConstantTemplate(each["album"]).resolve_data(var_dict)
        else:
            f["album"] = each["album"]
    if each.get("albumartist", None):
        if "${" in each["albumartist"]:
            f["albumartist"] = ConstantTemplate(each["albumartist"]).resolve_data(var_dict)
        else:
            f["albumartist"] = each["albumartist"]
    if each.get("discnumber", None):
        if "${" in each["discnumber"]:
            f["discnumber"] = ConstantTemplate(each["discnumber"]).resolve_data(var_dict)
        else:
            f["discnumber"] = each["discnumber"]
    if each.get("tracknumber", None):
        if "${" in each["tracknumber"]:
            f["tracknumber"] = ConstantTemplate(each["tracknumber"]).resolve_data(var_dict)
        else:
            f["tracknumber"] = each["tracknumber"]
    if each.get("genre", None):
        f["genre"] = each["genre"]
    if each.get("year", None):
        f["year"] = each["year"]
    if each.get("lyrics", None):
        f["lyrics"] = each["lyrics"]
        if each.get("is_save_lyrics_file", False):
            lyrics_file_path = f"{os.path.dirname(each['file_full_path'])}/{base_filename}.lrc"
            with open(lyrics_file_path, "w", encoding="utf-8") as f_lyc:
                f_lyc.write(each["lyrics"])
    else:
        if each.get("is_save_lyrics_file", False):
            lyrics_file_path = f"{os.path.dirname(each['file_full_path'])}/{base_filename}.lrc"
            if not os.path.exists(lyrics_file_path):
                with open(lyrics_file_path, "w", encoding="utf-8") as f_lyc2:
                    f_lyc2.write(f["lyrics"].value)
    if each.get("comment", None):
        f["comment"] = each["comment"]
    if each.get("album_img", None):
        try:
            img_data = send().GET(each["album_img"])
            if img_data.status_code == 200:
                f['artwork'] = img_data.content
                if len(img_data.content)/1024/1024 > 5:
                    f['artwork'] = f['artwork'].first.raw_thumbnail([2048, 2048])
                if is_raw_thumbnail:
                    f['artwork'] = f['artwork'].first.raw_thumbnail([2048, 2048])
        except Exception:
            pass
    f.save()
    # 重命名文件名称
    if each.get("filename", None):
        if "${" in each["filename"]:
            each["filename"] = ConstantTemplate(each["filename"]).resolve_data(var_dict)
        if not each["filename"].endswith(file_ext):
            each["filename"] = f"{each['filename']}.{file_ext}"
        parent_path = os.path.dirname(each["file_full_path"])
        os.rename(each["file_full_path"], f"{parent_path}/{each['filename']}")
