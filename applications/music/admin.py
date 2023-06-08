# -*- coding: utf-8 -*-
from django.contrib import admin, messages
from django.http import JsonResponse
from simpleui.admin import AjaxAdmin

from .models import Album, Track, Artist, Genre, Attachment, Playlist, TrackFavorite, Folder
from ..task.tasks import scan_folder, scan_music_id3


@admin.register(Album)
class AlbumAdmin(AjaxAdmin):
    list_display = (
        'id',
        'name',
        'artist',
        'max_year',
        'song_count',
        'plays_count',
        'duration',
        'genre',
        'created_at',
        'updated_at',
        'accessed_date',
        'full_text',
        'size',
    )
    list_filter = ()
    search_fields = ('name',)
    date_hierarchy = 'created_at'
    list_per_page = 10
    actions = ['merge_album']

    def merge_album(self, request, queryset):
        # 这里的queryset 会有数据过滤，只包含选中的数据

        post = request.POST
        # 这里获取到数据后，可以做些业务处理
        # post中的_action 是方法名
        # post中 _selected 是选中的数据，逗号分割
        if not post.get('_selected'):
            return JsonResponse(data={
                'status': 'error',
                'msg': '请先选中数据！'
            })
        else:
            name = post.get('name')
            first_album = queryset[0]
            first_album.name = name
            first_album.save()
            for album in queryset[1:]:
                Track.objects.filter(album=album).update(album=first_album)
                Album.objects.filter(id=album.id).delete()

            return JsonResponse(data={
                'status': 'success',
                'msg': '处理成功！'
            })

    merge_album.short_description = '合并专辑'
    merge_album.layer = {
        # 弹出层中的输入框配置

        # 这里指定对话框的标题
        'title': '合并专辑',
        # 提示信息
        'tips': '请输入合并后的专辑名称',
        # 确认按钮显示文本
        'confirm_button': '确认提交',
        # 取消按钮显示文本
        'cancel_button': '取消',

        # 弹出层对话框的宽度，默认50%
        'width': '40%',

        # 表单中 label的宽度，对应element-ui的 label-width，默认80px
        'labelWidth': "80px",
        'params': [{
            # 这里的type 对应el-input的原生input属性，默认为input
            'type': 'input',
            # key 对应post参数中的key
            'key': 'name',
            # 显示的文本
            'label': '专辑名称',
            # 为空校验，默认为False
            'require': True
        }]
    }


@admin.register(Track)
class TrackAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'path',
        'album',
        'artist',
        'has_cover_art',
        'track_number',
        'disc_number',
        'plays_count',
        'year',
        'size',
        'suffix',
        'mimetype',
        'duration',
        'bit_rate',
        'genre',
        'created_at',
        'updated_at',
        'accessed_date',
        'full_text',
    )
    list_filter = (
        'has_cover_art',
        'created_at',
        'updated_at',
        'accessed_date',
    )
    search_fields = ('name',)
    date_hierarchy = 'created_at'
    list_per_page = 10


@admin.register(Artist)
class ArtistAdmin(AjaxAdmin):
    list_display = (
        'id',
        'name',
        'album_count',
        'full_text',
        'song_count',
        'size',
        'mbz_artist_id',
        'attachment_cover',
        'similar_artists',
        'external_url',
        'external_info_updated_at',
    )
    list_filter = ()
    search_fields = ('name',)

    list_per_page = 10
    actions = ['merge_artist']

    def merge_artist(self, request, queryset):
        # 这里的queryset 会有数据过滤，只包含选中的数据

        post = request.POST
        # 这里获取到数据后，可以做些业务处理
        # post中的_action 是方法名
        # post中 _selected 是选中的数据，逗号分割
        if not post.get('_selected'):
            return JsonResponse(data={
                'status': 'error',
                'msg': '请先选中数据！'
            })
        else:
            name = post.get('name')
            first_artist = queryset[0]
            first_artist.name = name
            first_artist.save()
            for artist in queryset[1:]:
                Track.objects.filter(artist=artist).update(artist=first_artist)
                Album.objects.filter(artist=artist).update(artist=first_artist)
                Artist.objects.filter(id=artist.id).delete()

            return JsonResponse(data={
                'status': 'success',
                'msg': '处理成功！'
            })

    merge_artist.short_description = '合并歌手'
    merge_artist.layer = {
        # 弹出层中的输入框配置

        # 这里指定对话框的标题
        'title': '合并歌手',
        # 提示信息
        'tips': '请输入合并后的歌手名称',
        # 确认按钮显示文本
        'confirm_button': '确认提交',
        # 取消按钮显示文本
        'cancel_button': '取消',

        # 弹出层对话框的宽度，默认50%
        'width': '40%',

        # 表单中 label的宽度，对应element-ui的 label-width，默认80px
        'labelWidth': "80px",
        'params': [{
            # 这里的type 对应el-input的原生input属性，默认为input
            'type': 'input',
            # key 对应post参数中的key
            'key': 'name',
            # 显示的文本
            'label': '歌手名称',
            # 为空校验，默认为False
            'require': True
        }]
    }


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)


@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'url',
        'creation_date',
        'last_fetch_date',
        'size',
        'mimetype',
        'file',
    )
    list_filter = ('creation_date', 'last_fetch_date')


@admin.register(Playlist)
class PlaylistAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'user',
        'creation_date',
        'modification_date',
        'privacy_level',
    )
    list_filter = ('user', 'creation_date', 'modification_date')
    search_fields = ('name',)


@admin.register(TrackFavorite)
class TrackFavoriteAdmin(admin.ModelAdmin):
    list_display = ('id', 'creation_date', 'user', 'track')
    list_filter = ('creation_date', 'user', 'track')


@admin.register(Folder)
class FolderAdmin(AjaxAdmin):
    list_display = (
        'id',
        'name',
        'path',
        'created_at',
        'last_scan_time',
        'file_type',
        'uid',
        'parent_id',
    )
    list_filter = ("file_type", "state")
    search_fields = ('name',)
    date_hierarchy = 'created_at'
    list_per_page = 10
    actions = ['scan_folder_task', "scan_music_id3"]

    def scan_folder_task(self, request, queryset):
        scan_folder.delay()
        return JsonResponse(data={
            'status': 'success',
            'msg': '处理成功！'
        })

    scan_folder_task.short_description = '扫描文件'
    scan_folder_task.layer = {
        # 弹出层中的输入框配置

        # 这里指定对话框的标题
        'title': '扫描文件',
        # 提示信息
        'tips': '扫描挂载的音乐文件夹，会比较耗时，是否继续？',
        # 确认按钮显示文本
        'confirm_button': '确认提交',
        # 取消按钮显示文本
        'cancel_button': '取消',

        # 弹出层对话框的宽度，默认50%
        'width': '40%',

        # 表单中 label的宽度，对应element-ui的 label-width，默认80px
        'labelWidth': "80px",
        'params': []
    }

    def scan_music_id3(self, request, queryset):
        scan_music_id3.delay()
        return JsonResponse(data={
            'status': 'success',
            'msg': '处理成功！'
        })

    scan_music_id3.short_description = '扫描音乐'
    scan_music_id3.layer = {
        # 弹出层中的输入框配置

        # 这里指定对话框的标题
        'title': '扫描音乐',
        # 提示信息
        'tips': '扫描音乐的id3数据入库，会比较耗时，是否继续？',
        # 确认按钮显示文本
        'confirm_button': '确认提交',
        # 取消按钮显示文本
        'cancel_button': '取消',

        # 弹出层对话框的宽度，默认50%
        'width': '40%',

        # 表单中 label的宽度，对应element-ui的 label-width，默认80px
        'labelWidth': "80px",
        'params': []
    }
