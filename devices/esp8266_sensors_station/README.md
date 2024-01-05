# ESP8266 Sensor Station Service

Service manages ESP8266 Sensor Station device. It requests ESP8266 server. 
Data read from device are published to *sensors* collection in firestore.

## Install it from local environment

```bash
poetry add esp8266_sensors_station
```

## Usage

1. Download firebase certificate and name it as *firebase-certificate.json*
2. Copy *config.example.yaml* to *config.yaml* and correct data in file.
3. Run service:

    ```bash
    poetry add  python -m esp8266_sensors_station -f config.yaml
    ```
   
Both files *firebase-certificate.json* and *config.yaml* are added to *.gitignore* file.

## ESP8266 server

Soon...
