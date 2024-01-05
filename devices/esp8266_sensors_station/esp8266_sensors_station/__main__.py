"""Entry point of app."""

import sys
import signal
import argparse
import logging
from pathlib import Path
from typing import Union
from pytz import utc
from google.api_core.datetime_helpers import DatetimeWithNanoseconds
from dependency_injector.wiring import Provide, inject

from device_common_utils import services as common_services
from device_common_utils.models import Sensor, Actuator

from . import services as local_services
from .containers import Application


logger = logging.getLogger()


@inject
def signal_callback(
    _, __,
    requester_service: local_services.RequesterService = Provide[Application.requester_service]
) -> None:
    """Ctrl+C signal callback."""

    print()
    logger.info('See you!')

    requester_service.stop()

    sys.exit(0)


def update_sensor_document(data: Union[dict, None], firestore_service: common_services.FirestoreService) -> None:
    """Sends given data to firestore or skip sending if data are empty."""

    if data is not None:

        logger.info('Data read successfully.')
        logger.debug(f'Data: {data}')

        timestamp = DatetimeWithNanoseconds.now(utc)
        sensor = Sensor(name='Sensors Station', timestamp=timestamp, data=data)
        firestore_service.update(sensor)

        logger.info(f'Data saved successfully in document {firestore_service.sensor_id}.')

    else:

        logger.info('Data read unsuccessfully.')
        logger.debug(f'Data is None.')


@inject
def requester_callback(
    data: Union[dict, None],
    firestore_service: common_services.FirestoreService = Provide[Application.firestore_service]
) -> None:
    """Callback triggered periodically to get latest measurements from air purifier."""

    update_sensor_document(data, firestore_service)


@inject
def firestore_callback(
    actuator: Actuator,
    firestore_service: common_services.FirestoreService = Provide[Application.firestore_service],
    requester_service: local_services.RequesterService = Provide[Application.requester_service]
) -> None:
    """Callback triggered if firestore client detects any changes in remote firestore database."""

    logger.info(f'Change detected in document {firestore_service.actuator_id}')


@inject
def main(
    firestore_service: common_services.FirestoreService = Provide[Application.firestore_service],
    requester_service: local_services.RequesterService = Provide[Application.requester_service]
) -> None:
    """Main app function."""

    firestore_service.register_callback(firestore_callback)
    requester_service.register_callback(requester_callback)

    logger.info('Starting requester listener loop...')
    requester_service.loop()


if __name__ == "__main__":

    signal.signal(signal.SIGINT, signal_callback)

    parser = argparse.ArgumentParser(description='Sensor Station manager.')
    parser.add_argument('-f', '--file', type=str, help='Reads YAML configuration file.')
    args = parser.parse_args()

    if args.file is None or not Path(args.file).exists():
        raise FileNotFoundError(f'File does not exist: {args.file}')

    logger.info(f'Used configuration file: {args.file}')

    application = Application()
    application.config.from_yaml(args.file)
    application.init_resources()
    application.wire(modules=[__name__])

    main()
