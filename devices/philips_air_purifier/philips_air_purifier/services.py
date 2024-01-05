"""Services module."""

import time
from typing import Callable, Union
from philips_air_purifier_ac2889 import AirPurifier
from philips_air_purifier_ac2889.errors import AirPurifierError


class AirPurifierService:
    """Service to manage air purifier device."""

    def __init__(self, ip_address: str, checking_interval: int) -> None:
        self.ip_address = ip_address
        self.checking_interval = checking_interval
        self.is_running = False

        self._device = AirPurifier(host=self.ip_address)
        self._callback = None

    def register_callback(self, callback: Callable) -> None:
        """Creates callback triggered periodically."""

        self._callback = callback

    def set(self, **parameters: str) -> Union[None, dict]:
        """Sets given parameters in air purifier."""

        try:
            status = self._device.connect().set(**parameters)
        except AirPurifierError:
            status = None

        return status

    def get(self) -> Union[None, dict]:
        """Reads parameters from air purifier."""

        try:
            data = self._device.connect().get()
        except AirPurifierError:
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
