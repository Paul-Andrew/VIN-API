import fastapi
from vin2 import *
app = fastapi.FastAPI()


@app.on_event("startup")
async def startup():
    init_db()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

@app.on_event("")
def before_request():
    database.connect()

@app.after_request
def after_request(response):
    database.close()
    return response


@app.get('/lookup/{vin}')
async def lookup(vin):
    if not validate_vin(vin):
        return 400, f'VIN not valid: {vin}'
    return await get_for_vin(vin)


@app.delete('/remove/{vin}')
async def remove(vin):
    return await delete_vin(vin)
    # Return VIN and success/failure


@app.get('/export')
async def export():
    # TODO: Parquet Format!
    return await get_vins()
