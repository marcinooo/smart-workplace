import threading
from typing import Callable
from firebase_admin import firestore

from .models import Sensor, Actuator


class FirestoreService:
    """Service to manage given collection."""

    def __init__(self, db: firestore.client, actuator_id: str, sensor_id: str) -> None:

        self.db = db
        self.actuator_id = actuator_id
        self.sensor_id = sensor_id

        self._is_callback_done = threading.Event()

    def register_callback(self, callback: Callable) -> None:
        """Creates callback triggered on document update."""

        def safe_callback(doc_snapshot, _, __):
            """Callback with signature required by firestore."""
            try:
                for document in doc_snapshot:

                    if document.id == self.actuator_id:
                        actuator = Actuator.from_dict(document.to_dict())
                        callback(actuator)
                        break

                self._is_callback_done.set()
            except Exception as error:
                print(error)

        self.db.collection('actuators').document(self.actuator_id).on_snapshot(safe_callback)

    def update(self, sensor: Sensor) -> None:
        """Updates document by merging given data."""

        doc_ref = self.db.collection('sensors').document(self.sensor_id)
        doc_ref.set(sensor.to_dict(), merge=True)
