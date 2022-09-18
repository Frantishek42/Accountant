from datetime import datetime
from peewee import *

db = SqliteDatabase('database/accountant.db')


class BasesModel(Model):

    class Meta:
        database = db


class RegisterUser(BasesModel):
    """
    Таблица для добавления зарегистрированных пользователей
    """
    register_date = DateTimeField(default=datetime.now())
    user_id = IntegerField()
    first_name = CharField()
    private_date = IntegerField(default=0)
    private = BooleanField(default=False)

    class Meta:
        db_table = 'register_user'


class MergeWithUser(BasesModel):
    """
    Таблица для формирования объединенных пользователей
    """
    users_id = CharField()

    class Meta:
        db_table = 'merge_with_user'


class Profit(BasesModel):
    """
    Таблица содержит название прибыли
    """
    name = TextField()

    class Meta:
        db_table = 'profit'


class WalletProfit(BasesModel):
    """
    Таблица для добавления прибыли

    Argument:
        start_date: дата добавления выставляется автоматически
        user_id: устанавливается id пользователя с таблицы register_user
        profit_name: устанавливается id названия с таблицы profit
        money_card: карта
        money_cash: наличные
    """
    start_date = DateField(default=datetime.now())
    user_id = ForeignKeyField(RegisterUser, to_field='id', on_delete='cascade')
    profit_name = ForeignKeyField(Profit, to_field='id', related_name='fk_prof_wall', on_delete='cascade', )
    money_card = IntegerField()
    money_cash = IntegerField()

    class Meta:
        db_table = 'wallet_profit'
        order_by = 'start_date'


class Expenses(BasesModel):
    """
    Таблица содержит название затрат

    Argument:
        name: str = Название затрат
    """
    name = TextField()

    class Meta:
        db_table = 'expenses'
        order_by = 'name'


class WalletExpenses(BasesModel):
    """
    Таблица для добавления затрат

    Argument:
        start_date: дата добавления выставляется автоматически
        expenses_id: устанавливается id названия с таблицы expenses
        user_id: устанавливается id пользователя с таблицы register_user
        money_card: карта
        money_cash: наличные
    """
    start_date = DateField(default=datetime.now())
    expenses_id = ForeignKeyField(Expenses, to_field='id', related_name='fk_exp_wall', on_delete='cascade')
    user_id = ForeignKeyField(RegisterUser, to_field='id', on_delete='cascade')
    money_card = IntegerField()
    money_cash = IntegerField()

    class Meta:
        db_table = 'wallet_expenses'
        order_by = 'start_date'


class AutoPayment(BasesModel):
    """
    Таблица для добавления автоплатеж
    Argument:
        start_date: дата добавления выставляется автоматически
        user_id: устанавливается id пользователя с таблицы register_user
        name: названия платежа
        price: сумма списания
        day_of_debiting: день списания
        on_off: включения/отключения
    """
    start_date = DateField(default=datetime.now())
    user_id = ForeignKeyField(RegisterUser, to_field='id', on_delete='cascade')
    name = CharField(max_length=200)
    price = FloatField()
    day_of_debiting = IntegerField()
    on_off = BooleanField(default=True)

    class Meta:
        database = db
        db_table = 'auto_payment'


class WalletDB(BasesModel):
    """
    Таблица для формирования кошелька сколько денег в наличии

    Argument:
        user_id: устанавливается id пользователя с таблицы register_user
        money_card: карта
        money_cash: наличные
        money_credit: кредит
    """
    user_id = ForeignKeyField(RegisterUser, to_field='id', on_delete='cascade')
    money_card = IntegerField()
    money_cash = IntegerField()
    money_credit = IntegerField(default=0)

    class Meta:
        db_table = 'wallet'
