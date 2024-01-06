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
    air_purifier_service: local_services.AirPurifierService = Provide[Application.air_purifier_service]
) -> None:
    """Ctrl+C signal callback."""

    print()
    logger.info('See you!')

    air_purifier_service.stop()

    sys.exit(0)


def update_sensor_document(data: Union[dict, None], firestore_service: common_services.FirestoreService) -> None:
    """Sends given data to firestore or skip sending if data are empty."""

    if data is not None:

        logger.info('Data read successfully')
        logger.debug(f'Data: {data}')

        measurement = {'timestamp': DatetimeWithNanoseconds.now(utc), **data}
        sensor = Sensor(name='Philips Air Purifier', measurements=[measurement])
        firestore_service.update(sensor)

        logger.info(f'Data saved successfully in document {firestore_service.sensor_id}.')

    else:

        logger.info('Data read unsuccessfully')
        logger.debug(f'Data is None')


@inject
def air_purifier_callback(
    data: Union[dict, None],
    firestore_service: common_services.FirestoreService = Provide[Application.firestore_service]
) -> None:
    """Callback triggered periodically to get latest measurements from air purifier."""

    update_sensor_document(data, firestore_service)


@inject
def firestore_callback(
    actuator: Actuator,
    firestore_service: common_services.FirestoreService = Provide[Application.firestore_service],
    air_purifier_service: local_services.AirPurifierService = Provide[Application.air_purifier_service]
) -> None:
    """Callback triggered if firestore client detects any changes in remote firestore database."""

    logger.debug(f'Change detected in document {firestore_service.actuator_id}')
    logger.info(f'Received command: {actuator.command.action}')

    if actuator.command.action == 'SET':
        logger.debug(f'Data to set {actuator.command.data}')
        status = air_purifier_service.set(**actuator.command.data)
        logger.info(f'Data updated successfully on device')
        logger.debug(f'Status: {status}')

    else:
        logger.info(f'Command unknown')

    # Data are always refreshed (even if command is unknown)
    data = air_purifier_service.get()
    update_sensor_document(data, firestore_service)


@inject
def main(
    firestore_service: common_services.FirestoreService = Provide[Application.firestore_service],
    air_purifier_service: local_services.AirPurifierService = Provide[Application.air_purifier_service]
) -> None:
    """Main app function."""

    firestore_service.register_callback(firestore_callback)
    air_purifier_service.register_callback(air_purifier_callback)

    logger.info('Starting air purifier listener loop...')
    air_purifier_service.loop()


if __name__ == "__main__":

    signal.signal(signal.SIGINT, signal_callback)

    parser = argparse.ArgumentParser(description='Air Purifier manager.')
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
