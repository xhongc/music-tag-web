import os.path

from rest_framework import serializers

from applications.task.models import TaskRecord, Task


class FileListSerializer(serializers.Serializer):
    file_path = serializers.CharField(required=True)
    sorted_fields = serializers.ListField(required=True)


class Id3Serializer(serializers.Serializer):
    file_path = serializers.CharField(required=True)
    file_name = serializers.CharField(required=True)


class MusicId3Serializer(serializers.Serializer):
    title = serializers.CharField(required=True, allow_null=True, allow_blank=True)
    artist = serializers.CharField(required=True, allow_null=True, allow_blank=True)
    album = serializers.CharField(required=True, allow_null=True, allow_blank=True)
    album_type = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    language = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    albumartist = serializers.CharField(required=True, allow_null=True, allow_blank=True)
    discnumber = serializers.CharField(required=True, allow_null=True, allow_blank=True)
    tracknumber = serializers.CharField(required=True, allow_null=True, allow_blank=True)
    genre = serializers.CharField(required=True, allow_null=True, allow_blank=True)
    year = serializers.CharField(required=True, allow_null=True, allow_blank=True)
    lyrics = serializers.CharField(required=True, allow_null=True, allow_blank=True)
    is_save_lyrics_file = serializers.BooleanField(required=True)
    comment = serializers.CharField(required=True, allow_null=True, allow_blank=True)
    album_img = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    filename = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    file_full_path = serializers.CharField(required=True)


class UpdateId3Serializer(serializers.Serializer):
    music_id3_info = MusicId3Serializer(many=True)


class BatchUpdateId3Serializer(serializers.Serializer):
    file_full_path = serializers.JSONField(required=True)
    music_info = serializers.JSONField(required=True)
    select_data = serializers.JSONField(required=True)


class FetchId3ByTitleSerializer(serializers.Serializer):
    title = serializers.CharField(required=True)
    resource = serializers.CharField(required=True)
    full_path = serializers.CharField(required=False, allow_null=True, allow_blank=True)


class FetchLlyricSerializer(serializers.Serializer):
    song_id = serializers.CharField(required=True)
    resource = serializers.CharField(required=True)


class TranslationLycSerializer(serializers.Serializer):
    lyc = serializers.CharField(required=True)


class TidyFolderSerializer(serializers.Serializer):
    root_path = serializers.CharField(required=True)
    first_dir = serializers.CharField(required=True)
    second_dir = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    file_full_path = serializers.JSONField(required=True)
    select_data = serializers.JSONField(required=True)


class TaskSerializer(serializers.ModelSerializer):
    message = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = "__all__"

    def get_message(self, obj):
        return f"【{obj.song_name}】 未找到标签或修改失败！"

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        if os.path.exists(ret["full_path"]):
            ret["is_exists"] = True
        else:
            Task.objects.filter(id=ret["id"]).delete()
            ret["is_exists"] = False
        return ret
