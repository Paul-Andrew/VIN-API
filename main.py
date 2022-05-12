from fastapi import FastAPI, Depends, Response
from fastapi.exceptions import HTTPException
import requests
import re
from tempfile import NamedTemporaryFile
from urllib.parse import urljoin
from sqlalchemy import create_engine, Column, String, Boolean, select, insert, delete
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pandas import read_sql_table


# vin API config
DECODE_API_URL = 'https://vpic.nhtsa.dot.gov/api/vehicles/DecodeVinValues/'
DECODE_PARAMS = {'format': 'json'}
# \w allows underscore...
VIN_REGEX = "^[A-Za-z0-9]{17}$"


# DB Config
DB_URL = 'sqlite://'

engine = create_engine(DB_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def validate_vin(vin):
    # \w allows underscore...
    return re.match(VIN_REGEX, vin) is not None


def load_vin(vin):
    response = requests.get(
        urljoin(DECODE_API_URL, vin),
        params=DECODE_PARAMS
    )
    # Is it valid to return 429 if we get a 429?
    if response.status_code != 200:
        raise HTTPException(
            response.status_code,
            f"Error loading VIN Data:\n{response.text}"
        )

    results = response.json()['Results'][0]
    return results


class Vehicle(Base):
    __tablename__ = 'vehicles'
    vin = Column(String, primary_key=True, index=True)
    make = Column(String)
    model = Column(String)
    model_year = Column(String)
    body_class = Column(String)
    cached = Column(Boolean, default=False)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def column_names(self):
        return [c.name for c in self.__table__.columns]


Base.metadata.create_all(engine)


def get_db():
    db = None
    try:
        db = SessionLocal()
        yield db
    finally:
        if db is not None:
            db.close()


def map_api_to_db(api_vehicle, cached=True):
    # print(vehicle)
    db_vehicle = Vehicle(
        vin=api_vehicle['VIN'],
        make=api_vehicle['Make'],
        model=api_vehicle['Model'],
        model_year=api_vehicle['ModelYear'],
        body_class=api_vehicle['BodyClass'],
        cached=cached
    )
    # print(db_vehicle.as_dict())
    return db_vehicle


app = FastAPI(swagger_ui_parameters={"syntaxHighlight.theme": "obsidian"})


@app.get('/lookup/{vin}')
async def lookup(vin, db: Session = Depends(get_db)):
    """
    ### Lookup VIN Details
    VIN must be a 17 character string containing only alphanumeric characters.
    """
    if not validate_vin(vin):
        raise HTTPException(400, f'VIN not valid: {vin}')
    query = select(Vehicle).filter_by(vin=vin)
    vehicle = db.execute(query).first()
    if vehicle:
        return vehicle[0]
    else:
        api_vehicle = load_vin(vin)
        db_vehicle = map_api_to_db(api_vehicle)
        query = insert(Vehicle).values(**db_vehicle.as_dict())
        db.execute(query)
        db.commit()
        db_vehicle.cached = False
        return db_vehicle


@app.delete('/remove/{vin}')
async def remove(vin, db: Session = Depends(get_db)):
    """
    ### Remove VIN Details from Cache
    VIN must be a 17 character string containing only alphanumeric characters.
    """
    if not validate_vin(vin):
        raise HTTPException(400, f'VIN not valid: {vin}')
    query = select(Vehicle).filter_by(vin=vin)
    vehicle = db.execute(query).first()
    result = vehicle is not None
    if result:
        query = delete(Vehicle).where(Vehicle.vin == vin)
        db.execute(query)
        db.commit()
    return {'vin': vin, 'success': result}


@app.get('/export')
async def export(db: Session = Depends(get_db)):
    """
    ### Export VIN Details Cache
    Output in Parquet format.
    """
    f = NamedTemporaryFile()
    data = read_sql_table('vehicles', con=db.connection(), columns=Vehicle().column_names())
    pq = data.to_parquet(f.name)
    # TODO: Set a Mime-type when one is registered.
    # https://issues.apache.org/jira/browse/PARQUET-1889
    # TODO: Handle stream response for larger datasets
    return Response(f.read())
