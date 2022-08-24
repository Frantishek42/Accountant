from peewee import *

db = SqliteDatabase('database/profit.db')


class BasesModel(Model):
    user_id = IntegerField()
    start_date = DateField()
    money = IntegerField()

    class Meta:
        database = db
        order_by = 'user_id'


class Salary(BasesModel):

    class Meta:
        db_table = 'salary'


class PartTimeJob(BasesModel):

    class Meta:
        db_table = 'part_time_job'


class Sale(BasesModel):

    class Meta:
        db_table = 'sale'
