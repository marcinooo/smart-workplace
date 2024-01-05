"""Containers module."""

import logging.config
import firebase_admin
from dependency_injector import containers, providers
from firebase_admin import credentials
from firebase_admin import firestore

from device_common_utils import services as common_services

from . import services as local_services


class Application(containers.DeclarativeContainer):

    config = providers.Configuration()

    logging = providers.Resource(logging.config.dictConfig, config=config.logging)

    firebase_cred = providers.Singleton(credentials.Certificate, config.firebase.credentials)

    firebase_app = providers.Singleton(firebase_admin.initialize_app, firebase_cred)

    firestore_db = providers.Singleton(firestore.client, app=firebase_app)

    firestore_service = providers.Singleton(
        common_services.FirestoreService,
        db=firestore_db,
        actuator_id=config.firebase.actuator_id,
        sensor_id=config.firebase.sensor_id
    )

    air_purifier_service = providers.Singleton(
        local_services.AirPurifierService,
        ip_address=config.air_purifier.ip_address,
        checking_interval=config.air_purifier.checking_interval
    )
