# ETL - Extract, Transform, Load for sensor data

Sources for all ETL of the Smart Emission Platform. Originally this ETL was developed
for the Smart Emission Project Nijmegen and the Intemo Josene Sensor Device (2015-2017). 
As to accommodate other sensor devices like the [EU JRC AirSensEUR](http://www.airsenseur.org), the ETL-framework
has been generalized (2018). 

Uses deployment-specific variables for databases, passwords etc (not stored in GitHub).

All ETL is developed using [Stetl](http://stetl.org). Stetl is a Python framework and programming model for any ETL
process. The essence of Stetl is that each ETL process is a chain of linked Input, Filters and Output Python classes
specified in a Stetl Config File. 

The `.sh` files each invoke a Stetl ETL process via Docker using a Stetl config (`.cfg`) file specific
for that ETL process. Stetl is run via Docker. 

Additional Python files implement specific ETL modules not defined
in the Stetl Framework and are available under the Python [smartem](smartem) package.

All ETL processes are invoked using the same [SE Stetl Docker image](Dockerfile).
They can be scheduled via Kubernetes or `cron`.

The main ETL is multi-step as follows.

## Step 1: Harvesters - Fetching raw sensor data

The SE ETL follows a "pull" model: raw sensor data is "harvested" from data collector servers and other sensor networks.

The following ETL configs/processes:

- Harvester Whale: get all raw timeseries sensor-values from the [Whale API](../docs/specs/rawsensor-api/rawsensor-api.txt) for Intemo Jose sensor devices, see [harvester_whale.cfg](harvester_whale.cfg)
- Harvester Influx: get all raw timeseries sensor-values from an InfluxDB, initially for AirSensEUR (ASE) devices, see [harvester_influx.cfg](config/harvester_influx.cfg)

As a result all raw sensor-data is stored in PostGIS using the schema [db-schema-raw.sql](../database/schema/db-schema-raw.sql). 
The Raw Data fetched via the Harvesters is further processed in Step 2 Refiner.

## Step 2: Refiners

In this step all raw harvested timeseries data is "refined". Refinement involves the following:

- validation: remove outliers (pre and post)
- conversion: convert raw sensor values to standard units (e.g. temperature milliKelvin to degree Celsius)
- calibration: calibrate raw sensor gas-values to standard units using ANN (e.g. resistance/Ohm to AQ ug/m3 concentration)
- aggregation: make hourly average values for each sensor (''uurwaarden'')

See [refiner.cfg](config/refiner.cfg) and [smartem/refiner](smartem/refiner).
In particular the above steps are driven from the type of sensor device.
The learning process for ANN calibration is implemented under [smartem/calibrator](smartem/calibrator).

As a result of this step, sensor-data timeseries (hour-values) are
stored in PostGIS [db-schema-refined.sql](../database/schema/db-schema-refined.sql) AND in InfluxDB. 

## Step 3: Publishers

In this step all refined/aggregated timeseries data is published to various IoT/SWE services. 
The following publishers are present:

- SOSPublisher - publish to a remote SOS via SOS-T(ransactional) protocol [sospublisher.cfg](config/sospublisher.cfg)
- STAPublisher - publish to a remote SensorThings API (STA) via REST [stapublisher.cfg](config/stapublisher.cfg) 

All publication/output ETL uses plain Python string templates (no need for Jinja2 yet) with parameter 
substitution, e.g. [smartem/publisher/sostemplates](smartem/publisher/sostemplates) for SOS and [smartem/publisher/statemplates](smartem/publisher/statemplates) for STA. 

NB publication to WFS and WMS is not explicitly required: these services directly
use the timeseries refined tables and Postgres VIEWs from Step 2.

## Last Values

This step is special: it is a pass-through from the Raw Sensor API to a single
table with (refined) last values for all sensors for the SOS emulation API (sosemu).
This ETL process originated historically as no SOS and STA was initially available
but the project needed to develop the SmartApp with last values.

- Last: get and convert last sensor-values for all devices: [last.cfg](config/last.cfg).

As a result this raw sensor-data is stored in PostGIS [db-schema-last.sql](../database/schema/db-schema-last.sql).
 
## Calibration

(Currently only for Intemo Josene devices)

In order to collect reference data and generate the ANN Calibration Estimator, 
three additional ETL processes have been added later in the project (dec 2016):

- [Extractor](config/extractor.cfg): to extract raw (Jose) Sensor Values from the Harvested (Step 1) RawDBInput into InfluxDB
- [Harvester_RIVM](config/harvester_rivm.cfg): to extract calibrated gas samples (hour averages) from RIVM LML SOS into InfluxDB

The above two datasets in InfluxDB are used to generate the ANN Calibration Estimator object by running the Calibrator
ETL process:

- [Calibrator](config/calibrator.cfg): to read/merge RIVM and Jose values from InfluxDB to create the ANN Estimator object (pickled)

## Deployment

Deployment options per ETL process. This mainly involves setting the proper environment variables.
The convention is to use `stetl_` names for variable names in the [config files](config).
For example `pg_database` within [last.cfg](config/last.cfg) becomes `stetl_pg_database` within
a K8s or other Docker deployment.

## ETL process: Last (Values)

The following environment vars need to be set, either via `docker-compose` or
Kubernetes.

|Environment variable|
|---|
|stetl_raw_device_url_1|
|stetl_raw_device_url_2|
|stetl_intemo_token|
|stetl_pg_host|
|stetl_pg_database|
|stetl_pg_user|
|stetl_pg_password|
|stetl_pg_schema_rt|
|stetl_pg_schema_calibrated|
