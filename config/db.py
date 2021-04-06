
from django.conf import settings
from django.db import models, transaction, connections, utils
from django.contrib.auth.models import UserManager
from .mixins import ReadReplicaRoutingMixin


def get_connection(is_replica=False):
    if is_replica and settings.DB_HOST_REPLICA:
        db_alias_name = settings.DB_ALIAS_REPLICA
    else:
        db_alias_name = utils.DEFAULT_DB_ALIAS
    return connections[db_alias_name]


class BaseManager(models.Manager, ReadReplicaRoutingMixin):

    def __init__(self):
        super().__init__()


class BaseUserManager(UserManager, ReadReplicaRoutingMixin):

    def __init__(self):
        super().__init__()


class DatabaseRouter:

    @staticmethod
    def db_for_read(model, **hints):
        conn = transaction.get_connection(using=settings.DB_ALIAS_WRITE)
        if conn.in_atomic_block:
            return settings.DB_ALIAS_WRITE
        return settings.READ_DB_ALIAS

    @staticmethod
    def db_for_write(model, **hints):
        return settings.DB_ALIAS_WRITE

    @staticmethod
    def allow_relation(obj1, obj2, **hints):
        return True

    @staticmethod
    def allow_migrate(db, app_label, model_name=None, **hints):
        return True
