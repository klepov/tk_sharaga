import json

from peewee import *

db = SqliteDatabase('people.db')


class User(Model):
    is_granted = BooleanField()
    is_blocked = BooleanField()
    mask_password = CharField()
    name = CharField(unique=True)
    password = CharField()

    class Meta:
        database = db


try:
    User.create_table()
except OperationalError:
    pass


class MaskEqualsPassword(Exception):
    pass
