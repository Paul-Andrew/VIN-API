__all__: [

    'init_db',
    'get_for_vin',
    'get_vins',
    'delete_vin'
]
import peewee
DB_PATH = 'sqlite://'
db = peewee.SqliteDatabase(DB_PATH)


class Vehicle(peewee.Model):
    vin = peewee.CharField(primary_key=True)
    make = peewee.CharField()
    model = peewee.CharField()
    model_year = peewee.CharField()
    body_class = peewee.CharField()

    class Meta:
        database = db


def init_db():
    with db:
        db.create_tables([Vehicle])


async def get_for_vin(vin):
    pass


async def get_vins(vin):
    pass


async def delete_vin(vin):
    pass
