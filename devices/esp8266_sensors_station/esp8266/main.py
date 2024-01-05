"""Script runs simple socket server on esp8266 board under MicroPython."""

from time import sleep
from machine import Pin, Timer
from dht import DHT22
from microapi import MicroAPI, Response
from utils import APIData, load_credentials, critical_error


sleep(6)

credentials = load_credentials()

api_data = APIData()
dht = DHT22(Pin(14))
timer = Timer(-1)
api = MicroAPI(credentials["wlan_id"], credentials["wlan_pass"])
api_data = APIData()


def measure_condition(_):
    """Reads temperature and humidity from DHT sensor."""

    try:
        dht.measure()
        temperature = dht.temperature()
        humidity = dht.humidity()
        api_data.add(temperature, humidity)

    except Exception as error:
        print('Couldn\'t get measurements: {}'.format(error))
        api_data.add(None, None)


@api.route('/data')
def index(request):
    """Handler for endpoint to get sensor data."""

    return Response(api_data.get())



# Setup periodic callback
timer.init(period=10_000, mode=Timer.PERIODIC, callback=measure_condition)

# Run web api
try:
    api.connect()
    api.start()
except Exception as error:
    critical_error(str(error), Pin(16, Pin.OUT))
