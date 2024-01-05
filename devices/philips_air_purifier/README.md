# Air Purifier Service

Service manages Philips Air Purifier AC2889. It uses `philips-air-purifier-ac2889` package 
([link](https://github.com/marcinooo/philips-air-purifier/tree/main)).
Data read from device are published to *sensors* collection in firestore. 
If *actuators* collection will be updated it will update device settings.

## Install it from local environment

```bash
poetry add  philips-air-purifier
```

## Usage

1. Download firebase certificate and name it as *firebase-certificate.json*
2. Copy *config.example.yaml* to *config.yaml* and correct data in file.
3. Run service:

    ```bash
    poetry run python -m philips_air_purifier -f config.yaml
    ```
   
Both files *firebase-certificate.json* and *config.yaml* are added to *.gitignore* file.
