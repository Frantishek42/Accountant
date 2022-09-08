from peewee import *

db = SqliteDatabase('database/wallet.db')


class WalletDB(Model):
    money_card = IntegerField()
    money_cash = IntegerField()
    money_credit = IntegerField(default=0)

    class Meta:
        database = db
        db_table = 'wallet'
