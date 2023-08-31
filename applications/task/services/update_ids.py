import base64
import os

import music_tag
from music_tag import MetadataItem
from mutagen.flac import VCFLACDict
from mutagen.id3 import TXXX, ID3

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
    if each.get("artist", None) is not None:
        if "${" in each["artist"]:
            artist = ConstantTemplate(each["artist"]).resolve_data(var_dict)
        else:
            artist = each["artist"]
        artists = artist.split(",")
        f.set("artist", artists)
    if each.get("album", None) is not None:
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
        if each.get("lyrics") is not None:
            f.remove_tag("lyrics")
        if each.get("is_save_lyrics_file", False):
            lyrics_file_path = f"{os.path.dirname(each['file_full_path'])}/cover-{base_filename}.lrc"
            if not os.path.exists(lyrics_file_path):
                with open(lyrics_file_path, "w", encoding="utf-8") as f_lyc2:
                    f_lyc2.write(f["lyrics"].value)
    if each.get("comment", None):
        f["comment"] = each["comment"]
    if each.get("album_img", None):
        try:
            img_content = None
            if each["album_img"].startswith("http"):
                img_data = send().GET(each["album_img"])
                if img_data.status_code == 200:
                    img_content = img_data.content
            else:
                img_content = base64.b64decode(each["album_img"])
            if img_content:
                f['artwork'] = img_content
                if each.get("is_save_album_cover", False):
                    format_str = f['artwork'].value.format
                    album_cover_path = f"{os.path.dirname(each['file_full_path'])}/cover-{f['album']}.{format_str}"
                    if os.path.exists(album_cover_path):
                        os.remove(album_cover_path)
                    if not os.path.exists(album_cover_path):
                        with open(album_cover_path, "wb") as f_img:
                            f_img.write(img_content)
                if len(img_content) / 1024 / 1024 > 5:
                    f['artwork'] = f['artwork'].first.raw_thumbnail([2048, 2048])
                if is_raw_thumbnail:
                    f['artwork'] = f['artwork'].first.raw_thumbnail([2048, 2048])
        except Exception as e:
            print(e)
            pass
    else:
        if each.get("is_save_album_cover", False):
            format_str = f['artwork'].value.format
            album_cover_path = f"{os.path.dirname(each['file_full_path'])}/cover-{f['album']}.{format_str}"
            if not os.path.exists(album_cover_path):
                with open(album_cover_path, "wb") as f_img:
                    f_img.write(f['artwork'].value.raw)
    if each.get("album_type", None):
        if isinstance(f.mfile.tags, VCFLACDict):
            f.mfile.tags["RELEASETYPE"] = each["album_type"]
        elif isinstance(f.mfile.tags, ID3):
            f.mfile.tags["MusicBrainz Album Type"] = TXXX(encoding=3,
                                                          desc="MusicBrainz Album Type",
                                                          text=each["album_type"])
        else:
            raise Exception("未知的音乐文件类型")
    if each.get("language", None):
        if isinstance(f.mfile.tags, VCFLACDict):
            f.mfile.tags["LANGUAGE"] = each["language"]
        elif isinstance(f.mfile.tags, ID3):
            f.mfile.tags["LANGUAGE"] = TXXX(encoding=3,
                                            desc="LANGUAGE",
                                            text=each["language"])
        else:
            raise Exception("未知的音乐文件类型")
    f.save()
    # 重命名文件名称
    if each.get("filename", None):
        if "${" in each["filename"]:
            each["filename"] = ConstantTemplate(each["filename"]).resolve_data(var_dict)
        if not each["filename"].endswith(file_ext):
            each["filename"] = f"{each['filename']}.{file_ext}"
        parent_path = os.path.dirname(each["file_full_path"])
        if each["file_full_path"] != f"{parent_path}/{each['filename']}":
            os.rename(each["file_full_path"], f"{parent_path}/{each['filename']}")
