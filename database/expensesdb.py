from peewee import *

db = SqliteDatabase('database/expenses.db')


class BasesModel(Model):
    user_id = IntegerField()
    start_date = DateField()
    money = IntegerField()

    class Meta:
        database = db
        order_by = 'user_id'


class Products(BasesModel):

    class Meta:
        db_table = 'products'


class Alcohol(BasesModel):

    class Meta:
        db_table = 'alcohol'


class Chemistry(BasesModel):

    class Meta:
        db_table = 'chemistry'


class Communal(BasesModel):

    class Meta:
        db_table = 'communal'


class Credit(BasesModel):

    class Meta:
        db_table = 'credit'


class GasStation(BasesModel):

    class Meta:
        db_table = 'gas_station'


class Car(BasesModel):

    class Meta:
        db_table = 'car'


class OnlineStore(BasesModel):

    class Meta:
        db_table = 'online_store'


class Other(BasesModel):
    name = TextField()

    class Meta:
        db_table = 'other'
