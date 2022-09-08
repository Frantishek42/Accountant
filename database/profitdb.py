from datetime import datetime

from peewee import *

db = SqliteDatabase('database/profit.db')


class BasesModel(Model):

    class Meta:
        database = db
        order_by = 'user_id'


class Profit(BasesModel):
    name = TextField()

    class Meta:
        db_table = 'salary'


class WalletProfit(BasesModel):
    start_date = DateField(default=datetime.now())
    user_id = IntegerField()
    profit_name = ForeignKeyField(Profit, to_field='id', related_name='fk_prof_wall', on_delete='cascade', )
    money_card = IntegerField()
    money_cash = IntegerField()

    class Meta:
        db_table = 'wallet_profit'
