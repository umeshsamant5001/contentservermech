from django.db import models
from jsonfield import JSONField


# fetching data from "http://devposapi.prathamopenschool.org/api/AppList" url
class AppListFromServerData(models.Model):
    AppId = models.CharField(max_length=30, primary_key=True)
    AppName = models.CharField(max_length=100)
    ThumbUrl = models.URLField(max_length=700)
    AppDesc = models.TextField(blank=True, null=True)
    AppOrder = models.CharField(max_length=20, default='')
    DateUpdated = models.CharField(max_length=100, default='',
                                   null=True, blank=True)
    fileName = models.CharField(max_length=100, default='', null=True,
                                blank=True)

    @classmethod
    def create(cls, AppId, AppName, ThumbUrl, AppDesc, AppOrder, DateUpdated):
        applist_server_data = cls(AppId=AppId, AppName=AppName, ThumbUrl=ThumbUrl,
                                  AppDesc=AppDesc, AppOrder=AppOrder,
                                  DateUpdated=DateUpdated, fileName=fileName)

        return applist_server_data

    def __str__(self):
        return self.AppId


# filling local db of project from http://devposapi.prathamopenschool.org/Api/AppNodeDetailListByNode?id=<ids>
# at http://localhost:8000/channel/app_available/
class AppAvailableInDB(models.Model):
    applistfromserverdata = models.ForeignKey(AppListFromServerData, on_delete=models.CASCADE)
    NodeId = models.CharField(max_length=100, default='')
    NodeType = models.CharField(max_length=100, default='')
    NodeTitle = models.CharField(max_length=100, default='')
    JsonData = JSONField(default={}, blank=True)
    ParentId = models.CharField(max_length=100, blank=True, null=True)
    AppId = models.CharField(max_length=100, default='')
    DateUpdated = models.CharField(max_length=100, default='',
                                   null=True, blank=True)

    @classmethod
    def create(cls, NodeId, NodeType, NodeTitle, JsonData, ParentId, AppId, DateUpdated):
        app_data = cls(NodeId=NodeId, NodeType=NodeType, NodeTitle=NodeTitle, JsonData=JsonData,
                       ParentId=ParentId, AppId=AppId, DateUpdated=DateUpdated)
        return app_data

    def __str__(self):
        return self.NodeId


# filling the data of lstfiles from http://devposapi.prathamopenschool.org/Api/AppNodeDetailListByNode?id=<ids>
class FileDataToBeStored(models.Model):
    appavailableindb = models.ForeignKey(AppAvailableInDB, related_name='LstFileList', on_delete=models.CASCADE)
    FileId = models.IntegerField()
    NodeId = models.CharField(max_length=100)
    FileType = models.CharField(max_length=100)
    FileUrl = models.URLField(max_length=500)
    DateUpdated = models.CharField(
        max_length=100, null=True, blank=True, default='')
    fileName = models.CharField(max_length=100, default='', null=True,
                                blank=True)

    @classmethod
    def create(cls, FileId, NodeId, FileType, FileUrl, DateUpdated):
        file_data = cls(FileId=FileId, NodeId=NodeId, FileType=FileType, FileUrl=FileUrl,
                        DateUpdated=DateUpdated, fileName=fileName)

        return file_data

    def __str__(self):
        return str(self.FileId)


class FileUpload(models.Model):
    uploaded_file = models.FileField(upload_to='media/')


class JsonDataStorage(models.Model):
    JsonId      =     models.CharField(max_length=50, default='')
    NodeId      =     models.CharField(max_length=50, default='')
    JsonType    =     models.CharField(max_length=50, default='') 
    JsonData    =     JSONField(default={}, blank=True)
    DateUpdated =     models.CharField(max_length=100, default='',
                                   null=True, blank=True)

    @classmethod
    def create(cls, JsonId, NodeId, JsonType, JsonData, DateUpdated):
        json_data_storage = cls(JsonId=JsonId, NodeId=NodeId, JsonType=JsonType, JsonData=JsonData,
                       DateUpdated=DateUpdated)
        return json_data_storage

    def __str__(self):
        return self.JsonId