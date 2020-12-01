from rest_framework import serializers
from core.models import VillageDataStore, UsageData, DeskTopData


class VillageDataStoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = VillageDataStore
        fields = '__all__'


class UsageDataSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        many = kwargs.pop('many', True)
        super(UsageDataSerializer, self).__init__(many=many, *args, **kwargs)
        
    data = serializers.JSONField(default='\{\}')
    filter_name = serializers.CharField(default='enter filter')
    table_name = serializers.CharField(default='enter name')
    created_at = serializers.DateTimeField(read_only=True)
    
    class Meta:
        model = UsageData
        fields = (
			'id', 'data', 'filter_name', 'table_name', 'created_at',
            )


class DeskTopDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeskTopData
        fields = '__all__'
