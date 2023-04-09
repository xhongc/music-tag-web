import music_tag

from applications.utils.send import send


def update_music_info(music_id3_info, is_raw_thumbnail=False):
    for each in music_id3_info:
        f = music_tag.load_file(each["file_full_path"])
        if each.get("title", None):
            f["title"] = each["title"]
        if each.get("artist", None):
            f["artist"] = each["artist"]
        if each.get("album", None):
            f["album"] = each["album"]
        if each.get("genre", None):
            f["genre"] = each["genre"]
        if each.get("year", None):
            f["year"] = each["year"]
        if each.get("lyrics", None):
            f["lyrics"] = each["lyrics"]
        if each.get("comment", None):
            f["comment"] = each["comment"]
        if each.get("album_img", None):
            img_data = send().GET(each["album_img"])
            if img_data.status_code == 200:
                f['artwork'] = img_data.content
                if is_raw_thumbnail:
                    f['artwork'] = f['artwork'].first.raw_thumbnail([128, 128])
        f.save()
