from rest_framework import serializers
from channels.models import (AppListFromServerData, AppAvailableInDB,
                             FileDataToBeStored, FileUpload, JsonDataStorage)


class AppListSerializer(serializers.ModelSerializer):

    class Meta:
        model = AppListFromServerData
        # fields = ['AppId', 'AppName', 'ThumbUrl', 'AppDesc', 'AppOrder', 'DateUpdated']
        exclude = ['fileName']


class AppAvailableSerializer(serializers.ModelSerializer):

    class Meta:
        model = AppAvailableInDB
        exclude = ['id']


class FileDataSerializer(serializers.ModelSerializer):

    class Meta:
        model = FileDataToBeStored
        fields = ['FileId', 'NodeId', 'FileType', 'FileUrl', 'DateUpdated']
        # depth = 3


class AppNodeDetailListSerializer(serializers.ModelSerializer):
    LstFileList = FileDataSerializer(many=True, read_only=True)

    class Meta:
        model = AppAvailableInDB
        fields = ['NodeId', 'NodeType', 'NodeTitle','JsonData', 'ParentId',
                 'AppId', 'DateUpdated', 'LstFileList']
        

class FileUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileUpload
        fields = ['id', 'uploaded_file']


class JsonDataStorageSerializer(serializers.ModelSerializer):

    class Meta:
        model = JsonDataStorage
        fields = ['id', 'JsonId', 'NodeId', 'JsonType', 'JsonData', 'DateUpdated']
