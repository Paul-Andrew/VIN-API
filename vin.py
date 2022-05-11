# __all__: [
#     'database',
#     'create_all',
#     'get_for_vin',
#     'get_vins',
#     'delete_vin'
# ]
import requests
from urllib.parse import urljoin
import re
import databases
from sqlalchemy import MetaData, Table, Column, Integer, String, create_engine
from pydantic import BaseModel, Field
from typing_extensions import Annotated


DB_URL = 'sqlite:///vin_db'
DECODE_API_URL = 'https://vpic.nhtsa.dot.gov/api/vehicles/DecodeVinValues/'
DECODE_PARAMS = {'format': 'json'}
# \w allows underscore...
VIN_REGEX = "^[A-Za-z0-9]{17}$"


database = databases.Database(DB_URL)
meta = MetaData()


Vehicles = Table(
    'vehicles', meta,
    Column('id', Integer, primary_key=True),
    Column('vin', String),
    Column('make', String),
    Column('model', String),
    Column('model_year', String),
    Column('body_class', String)
)


def create_all():
    engine = create_engine(
        DB_URL, connect_args={"check_same_thread": False}
    )
    meta.create_all(engine)


def validate_vin(vin):
    # \w allows underscore...
    return re.match(VIN_REGEX, vin) is not None


class VehicleModel(BaseModel):
    vin: Annotated[str, Field(regex=VIN_REGEX, alias='VIN')]
    make: Annotated[str, Field(alias='Make')]
    model: Annotated[str, Field(alias='Model')]
    model_year: Annotated[str, Field(alias='ModelYear')]
    body_class: Annotated[str, Field(alias='BodyClass')]

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        extra = 'ignore'


class CachedVehicle(VehicleModel):
    cached_result = Field(default=False, alias='Cached Result')


async def get_vins():
    return await database.fetch_all(Vehicles.select())


def load_vin(vin):
    response = requests.get(
        urljoin(DECODE_API_URL, vin),
        params=DECODE_PARAMS
    )
    # Is it valid to return 429 if we get a 429?
    if response.status_code == 200:
        results = response.json()['Results'][0]
        # print(results)
        return results


def parse_vin(raw) -> dict:
    return VehicleModel.parse_obj(raw).dict()


def cache_vin(vehicle: dict):
    database.execute(Vehicles.insert(**vehicle))


@database.transaction(force_rollback=True)
async def get_for_vin(vin: str):
    vehicle = None
    v = Vehicles
    print(v.c)
    db_vehicle = await database.fetch_one(v.select(v.c == vin))

    if db_vehicle:
        vehicle = CachedVehicle().parse_obj(db_vehicle)
    else:
        vehicle = parse_vin(load_vin(vin))
        cache_vin(vehicle)
    return vehicle


async def delete_vin(vin):
    pass
