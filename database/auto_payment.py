from datetime import datetime
from peewee import *

db = SqliteDatabase('database/auto_payment.db')


class AutoPayment(Model):
    start_date = DateField(default=datetime.now())
    user_id = IntegerField()
    name = CharField(max_length=200)
    price = FloatField()
    day_of_debiting = IntegerField()
    on_off = BooleanField(default=True)

    class Meta:
        database = db
        db_table = 'auto_payment'
