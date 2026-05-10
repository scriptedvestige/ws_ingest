# Ecowitt Weather Ingest Service
I'll be using FastAP to create an API that listens for data being pushed from the Ecowitt console.  This data will consist of observations from the WS69 sensor array, soil moisture sensors, and lightning strike detector in my yard.

The API will run as a service on a Raspberry Pi and catch the data being pushed from the console.  It will then process the data and insert it into my weather_db running on my TimescaleDB container.

Data Flow:
Sensors > Ecowitt Console > Raspberry Pi > Database