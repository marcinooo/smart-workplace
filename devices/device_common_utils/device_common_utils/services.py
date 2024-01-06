import threading
from typing import Callable
from firebase_admin import firestore

from .models import Sensor, Actuator


class FirestoreService:
    """Service to manage given collection."""

    def __init__(self, db: firestore.client, actuator_id: str, sensor_id: str, max_measurements: int = 15) -> None:

        self.db = db
        self.actuator_id = actuator_id
        self.sensor_id = sensor_id
        self.max_measurements = max_measurements

        self._is_callback_done = threading.Event()

    def register_callback(self, callback: Callable) -> None:
        """Creates callback triggered on document update."""

        def safe_callback(doc_snapshot, _, __):
            """Callback with signature required by firestore."""

            for document in doc_snapshot:

                if document.id == self.actuator_id:
                    actuator = Actuator.from_dict(document.to_dict())
                    callback(actuator)
                    break

            self._is_callback_done.set()

        self.db.collection('actuators').document(self.actuator_id).on_snapshot(safe_callback)

    def update(self, sensor: Sensor) -> None:
        """Updates document by merging given data."""

        number_of_new_measurements = len(sensor.measurements)

        if number_of_new_measurements > self.max_measurements:
            raise ValueError(f'Number of measurements can\'t be greater then maximum number of measurements '
                             f'({self.max_measurements}) defined for Firestore servie.')

        doc_ref = self.db.collection('sensors').document(self.sensor_id)

        doc = doc_ref.get()
        measurements = doc.to_dict().get('measurements', []) if doc.exists else []

        if len(measurements) >= self.max_measurements:
            measurements = measurements[0 - (15 - number_of_new_measurements):]

        measurements.extend(sensor.measurements)

        sensor_data = sensor.to_dict()
        sensor_data['measurements'] = measurements

        doc_ref.set(sensor_data, merge=True)
