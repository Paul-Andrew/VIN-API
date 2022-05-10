from sqlalchemy import MetaData, Table, Column, Integer, String

meta = MetaData()

Vehicles = Table(
    'vehicles', meta,
    Column('id', Integer, primary_key=True),
    Column('VIN', String),
    Column('Make', String),
    Column('Model', String),
    Column('ModelYear', String),
    Column('BodyClass', String)
)
