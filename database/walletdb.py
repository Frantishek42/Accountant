from peewee import *

db = SqliteDatabase('database/wallet.db')


class WalletDB(Model):
    id = IntegerField(PrimaryKeyField)
    money = IntegerField()

    class Meta:
        database = db
        order_by = 'user_id'
        db_table = 'wallet'
