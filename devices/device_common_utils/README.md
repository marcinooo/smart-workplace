# Package with Firestore Service

Service manages Firestore database. 
Data passed to update method are published to corresponding document in *sensors* collection. 
If *actuators* collection will be updated it will call given callback.

## Install it from local environment

```bash
poetry add device-common-utils
```

## Usage

Package is dedicated for other services.
