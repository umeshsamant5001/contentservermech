from django.contrib import admin
from .models import AppListFromServerData, AppAvailableInDB, FileDataToBeStored

# Register your models here.
admin.site.register(AppListFromServerData)
admin.site.register(AppAvailableInDB)
admin.site.register(FileDataToBeStored)
