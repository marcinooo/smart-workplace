"""Services module."""

import time
import json
import requests
from typing import Callable, Union


class RequesterService:
    """Service to manage esp8266 server."""

    def __init__(self, ip_address: str, checking_interval: int) -> None:
        self.ip_address = ip_address
        self.checking_interval = checking_interval
        self.is_running = False

        self._callback = None

    def register_callback(self, callback: Callable) -> None:
        """Creates callback triggered periodically."""

        self._callback = callback

    def get(self) -> Union[None, dict]:
        """Reads parameters from device."""

        try:
            response = requests.get(f'http://{self.ip_address}/data')
        except (requests.exceptions.RequestException,
                requests.exceptions.TooManyRedirects,
                requests.exceptions.Timeout):
            data = None
        else:
            data = response.content.decode() if response.status_code == 200 else None

            try:
                data = json.loads(data)
            except ValueError:
                data = None

        return data

    def loop(self) -> None:
        """Runs infinite loop and call callback in given intervals."""

        self.is_running = True

        while self.is_running:

            data = self.get()
            self._callback(data)
            time.sleep(self.checking_interval)

    def stop(self) -> None:
        """Stops infinite loop."""

        self.is_running = False
