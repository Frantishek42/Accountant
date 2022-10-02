from datetime import datetime
from peewee import *
import time
from logger.log import logger

db = SqliteDatabase('database/accountant.db')


class BasesModel(Model):

    class Meta:
        database = db


class RegisterUser(BasesModel):
    """
    Таблица для добавления зарегистрированных пользователей
    Argument:
        register_date: дата регистрации пользователя выставляется автоматически
        user_id: добавляется id пользователя
        first_name: добавляется имя пользователя
    """
    register_date = DateTimeField(default=datetime.now())
    user_id = IntegerField()
    first_name = CharField()

    class Meta:
        db_table = 'register_user'


class UserSubscription(BasesModel):
    """
        Таблица для добавления пользователей которые оформили подписку
        Argument:
            user_id: добавляется id user_id с таблицы register_user
            private_date: дата покупки подписки
            private_date: кол-во дней подписки
            private: подключения подписки

        """
    user_id = ForeignKeyField(RegisterUser, to_field='id', on_delete='cascade')
    time_sub = TimeField()

    class Meta:
        db_table = 'user_private'
        order_by = ['private_date']

    def get_time_sub(self, user_id):
        id_user_id = RegisterUser.get(RegisterUser.user_id == user_id)
        try:
            time_sub = self.get(UserSubscription.user_id == id_user_id)
            if int(time_sub.time_sub) >= int(time.time()):
                return True
        except DoesNotExist as exc:
            logger.info(f'Таблица подписки ')


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
    user_id = ForeignKeyField(RegisterUser, to_field='id', on_delete='cascade')

    class Meta:
        db_table = 'expenses'
        order_by = ['name']


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
        order_by = 'name'


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
