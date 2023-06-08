import uuid
from datetime import datetime

from django.contrib.auth.models import User
from django.db import models
from django_mysql.models import ListTextField

from applications.music import validators
from applications.music.utils import get_file_path


class Album(models.Model):
    name = models.CharField("专辑名称", max_length=255, default='', null=False)
    artist = models.ForeignKey('Artist', on_delete=models.SET_NULL, null=True, related_name='albums',
                               db_constraint=False)
    all_artist_ids = ListTextField(base_field=models.IntegerField(), default=list, null=True, blank=True)

    max_year = models.IntegerField(default=0, null=False)
    song_count = models.IntegerField("歌曲统计", default=-1, null=False)
    plays_count = models.IntegerField("播放次数", default=0, null=False)
    duration = models.FloatField("歌曲时长s", default=0, null=False)
    genre = models.ForeignKey('Genre', on_delete=models.SET_NULL, null=True, related_name='albums', db_constraint=False)
    created_at = models.DateTimeField(null=True, default=datetime.now)
    updated_at = models.DateTimeField(null=True, auto_now=True)
    accessed_date = models.DateTimeField("访问时间", null=True, blank=True)

    full_text = models.CharField(max_length=255, default='', null=True, blank=True)
    size = models.IntegerField("文件大小", default=0, null=False)
    comment = models.CharField(max_length=255, null=True, blank=True)
    paths = models.CharField(max_length=255, null=True, blank=True)
    description = models.CharField(max_length=255, default='', null=True, blank=True)
    attachment_cover = models.ForeignKey('Attachment', on_delete=models.SET_NULL, null=True, related_name='album_cover',
                                         db_constraint=False)

    # musicbrainz fields
    mbz_album_id = models.CharField(max_length=255, null=True, blank=True)
    mbz_album_artist_id = models.CharField(max_length=255, null=True, blank=True)
    mbz_album_type = models.CharField(max_length=255, null=True, blank=True)
    mbz_album_comment = models.CharField(max_length=255, null=True, blank=True)

    external_url = models.CharField(max_length=255, default='', null=True, blank=True)
    external_info_updated_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "专辑"
        verbose_name_plural = "专辑"

    def __str__(self):
        return self.name


class Track(models.Model):
    name = models.CharField(default='', max_length=255)

    path = models.CharField(default='', max_length=255)
    album = models.ForeignKey('Album', on_delete=models.SET_NULL, null=True, related_name='tracks', db_constraint=False)
    artist = models.ForeignKey('Artist', on_delete=models.SET_NULL, null=True, related_name='tracks',
                               db_constraint=False)
    has_cover_art = models.BooleanField(default=False)
    track_number = models.IntegerField(default=0)
    disc_number = models.IntegerField(default=0)
    plays_count = models.IntegerField("播放量", default=0, null=True)
    year = models.IntegerField(default=0, null=True)
    size = models.IntegerField("文件大小", default=0, null=False)
    suffix = models.CharField("后缀", default='', max_length=255, null=True)
    mimetype = models.CharField(default='', max_length=255, null=True)
    duration = models.FloatField("歌曲时长s", default=0, null=False)
    bit_rate = models.IntegerField(default=0, null=True)
    genre = models.ForeignKey('Genre', on_delete=models.SET_NULL, null=True, related_name='tracks', db_constraint=False)
    created_at = models.DateTimeField(null=True, auto_now_add=True)
    updated_at = models.DateTimeField(null=True, auto_now=True)
    accessed_date = models.DateTimeField("访问时间", null=True)
    full_text = models.CharField(default='', max_length=255, null=True, blank=True)
    comment = models.TextField(null=True)
    lyrics = models.TextField(null=True)
    # musicbrainz fields
    mbz_track_id = models.CharField(default='', max_length=255, null=True, blank=True)
    mbz_album_id = models.CharField(default='', max_length=255, null=True, blank=True)
    mbz_artist_id = models.CharField(default='', max_length=255, null=True, blank=True)
    mbz_album_artist_id = models.CharField(default='', max_length=255, null=True, blank=True)
    mbz_album_type = models.CharField(default='', max_length=255, null=True, blank=True)
    mbz_album_comment = models.CharField(default='', max_length=255, null=True, blank=True)
    mbz_release_track_id = models.CharField(default='', max_length=255, null=True, blank=True)

    class Meta:
        verbose_name = "歌曲"
        verbose_name_plural = "歌曲"

    def __str__(self):
        return self.name


class Artist(models.Model):
    name = models.CharField(max_length=255, default='', blank=False)
    album_count = models.IntegerField(default=0)
    full_text = models.CharField(max_length=255, default='', null=True, blank=True)

    song_count = models.IntegerField(default=0, null=True, blank=True)
    size = models.IntegerField(default=0, null=True, blank=True)
    mbz_artist_id = models.CharField(max_length=255, null=True, blank=True)
    attachment_cover = models.ForeignKey('Attachment', null=True, blank=True, on_delete=models.SET_NULL,
                                         related_name='artist_cover')

    similar_artists = models.CharField(max_length=255, default='', null=True, blank=True)
    external_url = models.CharField(max_length=255, default='', null=True, blank=True)
    external_info_updated_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "艺术家"
        verbose_name_plural = "艺术家"

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        verbose_name = "风格"
        verbose_name_plural = "风格"

    def __str__(self):
        return self.name


class Attachment(models.Model):
    # Remote URL where the attachment can be fetched
    url = models.URLField(max_length=500, null=True, blank=True)
    # Actor associated with the attachment
    creation_date = models.DateTimeField(default=datetime.now)
    last_fetch_date = models.DateTimeField(null=True, blank=True)
    # File size
    size = models.IntegerField(null=True, blank=True)
    mimetype = models.CharField(null=True, blank=True, max_length=200)

    file = models.ImageField(
        upload_to=get_file_path,
        max_length=255,
        validators=[
            validators.ImageDimensionsValidator(min_width=50, min_height=50),
            validators.FileValidator(
                allowed_extensions=["png", "jpg", "jpeg"],
                max_size=1024 * 1024 * 5,
            ),
        ],
    )

    def save(self, **kwargs):
        if self.file and not self.size:
            self.size = self.file.size

        if self.file and not self.mimetype:
            self.mimetype = ""

        return super().save()

    def __str__(self):
        return self.file.name

    class Meta:
        verbose_name = "附件"
        verbose_name_plural = "附件"


class Playlist(models.Model):
    PRIVACY_LEVEL_CHOICES = [
        ("me", "Only me"),
        ("followers", "Me and my followers"),
        ("instance", "Everyone on my instance, and my followers"),
        ("everyone", "Everyone, including people on other instances"),
    ]
    name = models.CharField(max_length=50)
    user = models.ForeignKey(User, related_name="playlists", on_delete=models.CASCADE)
    creation_date = models.DateTimeField(default=datetime.now)
    modification_date = models.DateTimeField(auto_now=True)
    privacy_level = models.CharField(max_length=30, choices=PRIVACY_LEVEL_CHOICES, default="instance")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "播放列表"
        verbose_name_plural = "播放列表"


class TrackFavorite(models.Model):
    creation_date = models.DateTimeField(default=datetime.now)
    user = models.ForeignKey(
        User, related_name="track_favorites", on_delete=models.CASCADE
    )
    track = models.ForeignKey(
        Track, related_name="track_favorites", on_delete=models.CASCADE, null=True, blank=True
    )
    album = models.ForeignKey(Album, related_name="track_favorites", on_delete=models.CASCADE, null=True, blank=True)
    artist = models.ForeignKey(Artist, related_name="track_favorites", on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        ordering = ("-creation_date",)
        verbose_name = "喜爱列表"
        verbose_name_plural = "喜爱列表"

    @classmethod
    def add_track(cls, track, user):
        favorite, created = cls.objects.get_or_create(user=user, track=track)
        return favorite

    @classmethod
    def add_album(cls, album, user):
        favorite, created = cls.objects.get_or_create(user=user, album=album)
        return favorite

    @classmethod
    def add_artist(cls, artist, user):
        favorite, created = cls.objects.get_or_create(user=user, artist=artist)
        return favorite


class Folder(models.Model):
    FILE_TYPE_CHOICES = (
        ('folder', '文件夹'),
        ('music', '音乐'),
        ('image', '图片'),
    )
    STATE_CHOICES = (
        ('none', '未扫描'),
        ('scanning', '扫描中'),
        ('scanned', '扫描完成'),
        ('updated', '已更新')
    )
    name = models.CharField("文件名称", max_length=256)
    path = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    last_scan_time = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(default=datetime.now)
    # 文件格式，例如：folder, music, image
    file_type = models.CharField("文件格式", max_length=32, default='folder', choices=FILE_TYPE_CHOICES)
    uid = models.UUIDField(default=uuid.uuid4, editable=False)
    parent_id = models.UUIDField(default=uuid.uuid4, editable=False, null=True, blank=True)
    # none, scanning, scanned, updated
    state = models.CharField("状态", max_length=32, default='none', choices=STATE_CHOICES)

    class Meta:
        verbose_name = "文件目录"
        verbose_name_plural = "文件目录"
