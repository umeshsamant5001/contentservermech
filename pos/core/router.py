class ChannelRouter:

    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'channels':
            return 'channels_db'
        return 'default'

    def db_for_write(self, model, **hints):
        if model._meta.app_label == 'channels':
            return 'channels_db'
        return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        if obj1._meta.app_label == 'channels' or obj2._meta.app_label == 'channels':
            return True
        elif 'channels' not in [obj1._meta.app_label, obj2._meta.app_label]:
            return True
        return False

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label == 'channels':
            return db == 'channels_db'
        return None