from django.db import models
from jsonfield import JSONField


# storing village, crl, student and group data in this model
# all the data inside this model is stored according to village selected with
# unique id of village referred as key_id
class VillageDataStore(models.Model):
    data = JSONField(default={}, blank=True)
    filter_name = models.CharField(max_length=100, default="Enter filter name")
    table_name = models.CharField(max_length=100, default="Enter table name")
    key_id = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    @classmethod
    def create(cls, data, filter_name, table_name, key_id):
        village_data = cls(data=data, filter_name=filter_name,
                           table_name=table_name, key_id=key_id)
        return village_data


class UsageData(models.Model):
    data = JSONField(default={}, blank=True)
    filter_name = models.CharField(max_length=100, default="Enter filter name")
    table_name = models.CharField(max_length=100, default="Enter table name")
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
