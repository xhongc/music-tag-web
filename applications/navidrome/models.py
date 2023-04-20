from django.db import models


class Album(models.Model):
    id = models.CharField(max_length=255, primary_key=True)
    name = models.CharField(max_length=255, default='', null=False)
    artist_id = models.CharField(max_length=255, default='', null=False)
    embed_art_path = models.CharField(max_length=255, default='', null=False)
    artist = models.CharField(max_length=255, default='', null=False)
    album_artist = models.CharField(max_length=255, default='', null=False)
    min_year = models.IntegerField(default=0, null=False)
    max_year = models.IntegerField(default=0, null=False)
    compilation = models.BooleanField(default=False, null=False)
    song_count = models.IntegerField(default=0, null=False)
    duration = models.FloatField(default=0, null=False)
    genre = models.CharField(max_length=255, default='', null=False)
    created_at = models.DateTimeField(null=True)
    updated_at = models.DateTimeField(null=True)
    full_text = models.CharField(max_length=255, default='', null=False)
    album_artist_id = models.CharField(max_length=255, default='', null=False)
    order_album_name = models.CharField(max_length=255)
    order_album_artist_name = models.CharField(max_length=255)
    sort_album_name = models.CharField(max_length=255)
    sort_artist_name = models.CharField(max_length=255)
    sort_album_artist_name = models.CharField(max_length=255)
    size = models.IntegerField(default=0, null=False)
    mbz_album_id = models.CharField(max_length=255, null=True)
    mbz_album_artist_id = models.CharField(max_length=255, null=True)
    mbz_album_type = models.CharField(max_length=255, null=True)
    mbz_album_comment = models.CharField(max_length=255, null=True)
    catalog_num = models.CharField(max_length=255, null=True)
    comment = models.CharField(max_length=255, null=True)
    all_artist_ids = models.CharField(max_length=255, null=True)
    image_files = models.CharField(max_length=255, null=True)
    paths = models.CharField(max_length=255, null=True)
    description = models.CharField(max_length=255, default='', null=False)
    small_image_url = models.CharField(max_length=255, default='', null=False)
    medium_image_url = models.CharField(max_length=255, default='', null=False)
    large_image_url = models.CharField(max_length=255, default='', null=False)
    external_url = models.CharField(max_length=255, default='', null=False)
    external_info_updated_at = models.DateTimeField(null=True)

    class Meta:
        db_table = "album"
        managed = False
        verbose_name = "专辑"
        verbose_name_plural = "专辑"


class MediaFile(models.Model):
    id = models.CharField(primary_key=True, max_length=255)
    path = models.CharField(default='', max_length=255)
    title = models.CharField(default='', max_length=255)
    album = models.CharField(default='', max_length=255)
    artist = models.CharField(default='', max_length=255)
    artist_id = models.CharField(default='', max_length=255)
    album_artist = models.CharField(default='', max_length=255)
    album_id = models.CharField(default='', max_length=255)
    has_cover_art = models.BooleanField(default=False)
    track_number = models.IntegerField(default=0)
    disc_number = models.IntegerField(default=0)
    year = models.IntegerField(default=0)
    size = models.IntegerField(default=0)
    suffix = models.CharField(default='', max_length=255)
    duration = models.FloatField(default=0)
    bit_rate = models.IntegerField(default=0)
    genre = models.CharField(default='', max_length=255)
    compilation = models.BooleanField(default=False)
    created_at = models.DateTimeField(null=True)
    updated_at = models.DateTimeField(null=True)
    full_text = models.CharField(default='', max_length=255)
    album_artist_id = models.CharField(default='', max_length=255)
    order_album_name = models.CharField(default='', max_length=255)
    order_album_artist_name = models.CharField(default='', max_length=255)
    order_artist_name = models.CharField(default='', max_length=255)
    sort_album_name = models.CharField(default='', max_length=255)
    sort_artist_name = models.CharField(default='', max_length=255)
    sort_album_artist_name = models.CharField(default='', max_length=255)
    sort_title = models.CharField(default='', max_length=255)
    disc_subtitle = models.CharField(default='', max_length=255)
    mbz_track_id = models.CharField(default='', max_length=255)
    mbz_album_id = models.CharField(default='', max_length=255)
    mbz_artist_id = models.CharField(default='', max_length=255)
    mbz_album_artist_id = models.CharField(default='', max_length=255)
    mbz_album_type = models.CharField(default='', max_length=255)
    mbz_album_comment = models.CharField(default='', max_length=255)
    catalog_num = models.CharField(default='', max_length=255)
    comment = models.TextField(null=True)
    lyrics = models.TextField(null=True)
    bpm = models.IntegerField(null=True)
    channels = models.IntegerField(null=True)
    order_title = models.CharField(default='', max_length=255, null=True)
    mbz_release_track_id = models.CharField(default='', max_length=255)
    rg_album_gain = models.FloatField(null=True)
    rg_album_peak = models.FloatField(null=True)
    rg_track_gain = models.FloatField(null=True)
    rg_track_peak = models.FloatField(null=True)

    class Meta:
        db_table = "media_file"
        managed = False
        verbose_name = "歌曲"
        verbose_name_plural = "歌曲"


class Artist(models.Model):
    id = models.CharField(max_length=255, primary_key=True)
    name = models.CharField(max_length=255, default='', blank=False)
    album_count = models.IntegerField(default=0)
    full_text = models.CharField(max_length=255, default='')
    order_artist_name = models.CharField(max_length=255)
    sort_artist_name = models.CharField(max_length=255)
    song_count = models.IntegerField(default=0)
    size = models.IntegerField(default=0)
    mbz_artist_id = models.CharField(max_length=255)
    biography = models.CharField(max_length=255, default='', blank=False)
    small_image_url = models.CharField(max_length=255, default='', blank=False)
    medium_image_url = models.CharField(max_length=255, default='', blank=False)
    large_image_url = models.CharField(max_length=255, default='', blank=False)
    similar_artists = models.CharField(max_length=255, default='', blank=False)
    external_url = models.CharField(max_length=255, default='', blank=False)
    external_info_updated_at = models.DateTimeField(null=True)

    class Meta:
        db_table = "artist"
        managed = False
        verbose_name = "艺术家"
        verbose_name_plural = "艺术家"


class Genre(models.Model):
    id = models.CharField(primary_key=True, max_length=255)
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        db_table = "genre"
        managed = False
        verbose_name = "风格"
        verbose_name_plural = "风格"
