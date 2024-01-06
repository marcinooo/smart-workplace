from dataclasses import dataclass, asdict
from google.api_core.datetime_helpers import DatetimeWithNanoseconds


class Document:

    def __init__(self, *args, **kwargs):
        pass

    def to_dict(self):
        """Dumps instance to dict."""

        return asdict(self)

    @classmethod
    def from_dict(cls, source: dict):
        """Creates instance based on given dictionary."""

        return cls(**source)


@dataclass
class ActuatorCommand:
    action: str
    data: dict
    timestamp: DatetimeWithNanoseconds


@dataclass
class Actuator(Document):
    """Represents actuator in ODM."""

    name: str
    command: ActuatorCommand

    def __post_init__(self):
        if isinstance(self.command, dict):
            self.command = ActuatorCommand(**self.command)


@dataclass
class Sensor(Document):
    """Represents sensor in ODM."""

    name: str
    measurements: list[dict]
