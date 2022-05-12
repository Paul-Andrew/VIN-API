from behave import given, when, then
import requests


server_path = "http://127.0.0.1:8888/"
test_vins = [
    "1XPWD40X1ED215307",
    "1XKWDB0X57J211825",
    "1XP5DB9X7YN526158",
    "4V4NC9EJXEN171694",
    "1XP5DB9X7XD487964"
]


def lookup(vin):
    return requests.get(server_path + 'lookup/' + vin)


def remove(vin):
    return requests.delete(server_path + 'remove/' + vin)


def export():
    return requests.get(server_path + 'export/')


@when(u'user accesses lookup endpoint with a new VIN')
def lookup_vin(context):
    context.vin = test_vins[0]
    context.response = lookup(context.vin)


@then(u'endpoint should respond with vehicle info')
def check_response(context):
    assert context.response.status_code == 200
    data = context.response.json()
    assert len(data.keys()) == 6
    assert data['vin'] == context.vin


@then(u'vehicle info should indicate the data was not cached')
def step_impl(context):
    assert context.response.status_code == 200
    assert context.response.json()['cached'] is False


@when(u'user accesses lookup endpoint with a invalid VIN')
def step_impl(context):
    context.vin = '32-10948123'
    context.response = lookup(context.vin)


@then(u'server should respond with 400 Client Error')
def step_impl(context):
    assert context.response.status_code == 400


@given(u'vehicle info is in cache')
def step_impl(context):
    lookup_vin(context)
    check_response(context)


@then(u'vehicle info should indicate the data was cached')
def step_impl(context):
    assert context.response.status_code == 200
    assert context.response.json()['cached'] is True


@when(u'user accesses remove endpoint with a new VIN')
def step_impl(context):
    context.vin = test_vins[0]
    context.response = remove(context.vin)
    print(f'sc: {context.response.status_code}')


@then(u'endpoint should respond with success: false.')
def step_impl(context):
    print(f'sc: {context.response.status_code}')
    assert context.response.status_code == 200
    print(context.response.json())
    assert context.response.json()['success'] is False


@then(u'response should include VIN')
def step_impl(context):
    assert context.response.status_code == 200
    data = context.response.json()
    assert data['vin'] == context.vin


@then(u'endpoint should respond with success: true.')
def step_impl(context):
    assert context.response.status_code == 200
    assert context.response.json()['success'] is True


@when(u'user accesses remove endpoint with a invalid VIN')
def step_impl(context):
    context.vin = "A234AALKDJF"
    context.response = remove(context.vin)


@when(u'user accesses export endpoint')
def step_impl(context):
    context.response = export()


@then(u'server should respond with empty Parquet')
def step_impl(context):
    assert context.response.status_code == 200
    assert context.response.raw
    # TODO: Better Parquet paring test


@given(u'another vehicle\'s info is in cache')
def step_impl(context):
    context.vin2 = test_vins[1]
    context.response = lookup(context.vin2)
    assert context.response.status_code == 200
    data = context.response.json()
    assert len(data.keys()) == 6
    assert data['vin'] == context.vin2


@then(u'server should respond with both vehicles in Parquet format')
def step_impl(context):
    assert context.response.status_code == 200
    assert context.response.raw
    # TODO: Better Parquet paring test
