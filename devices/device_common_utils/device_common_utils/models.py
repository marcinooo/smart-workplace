from dataclasses import dataclass, asdict
from google.api_core.datetime_helpers import DatetimeWithNanoseconds


@dataclass
class Document:

    name: str
    timestamp: DatetimeWithNanoseconds
    data: dict

    def to_dict(self):
        """Dumps instance to dict."""

        return asdict(self)

    @staticmethod
    def from_dict(source: dict):
        """Creates instance based on given dictionary."""

        return Document(**source)


class Actuator(Document):
    """Represents actuator in ODM."""


class Sensor(Document):
    """Represents sensor in ODM."""
