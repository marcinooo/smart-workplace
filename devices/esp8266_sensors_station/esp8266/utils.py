"""Set of helpers."""

import json
import time


class APIData:
    """
    Stores data served by api. 
    It adds a control number to identify data updates.
    """

    def __init__(self):
        self._payload = {
            'temperature': None,
            'humidity': None,
            'control_number': time.time()    
        }

    def get(self):
        """Returns ready to send data."""

        return self._payload

    def add(self, temperature, humidity):
        """Adds given data."""

        self._payload['temperature'] = temperature
        self._payload['humidity'] = humidity
        self._payload['control_number'] = time.time()


def load_credentials():
    """Loads credentials from JSON file."""

    with open('cred.json', 'r') as fh:
        return json.load(fh)


def critical_error(error, pin):
    """Save and signal critical error."""

    with open('critical_error.txt', 'w') as fh:
        fh.write(error)

    while True:
        pin.on()
        time.sleep_ms(500)
        pin.off()
        time.sleep_ms(500)
