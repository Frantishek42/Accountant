from datetime import datetime
from peewee import *

db = SqliteDatabase('database/expenses.db')


class BasesModel(Model):

    class Meta:
        database = db


class Expenses(BasesModel):
    name = TextField()

    class Meta:
        db_table = 'expenses'
        order_by = 'name'


class WalletExpenses(BasesModel):
    start_date = DateField(default=datetime.now())
    expenses_id = ForeignKeyField(Expenses, to_field='id', related_name='fk_exp_wall', on_delete='cascade')
    user_id = IntegerField()
    money_card = IntegerField()
    money_cash = IntegerField()

    class Meta:
        db_table = 'wallet_expenses'
        order_by = 'start_date'



