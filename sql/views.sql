-- Weather Station Observations
create or replace view ws_observations_view as select time as starttime, tempf as temp, humidity, windspeedmph as windspeed, eventrainin as rain from ws_observations order by time;

-- Office Observations
create or replace view office_obs_view as select time as starttime, temp2f as temp, humidity2 as humidity from office_obs order by time;

-- Console Observations
create or replace view console_obs_view as select time as starttime, tempinf as temp, humidityin as humidity from console_obs order by time;

-- Barometric Pressure
create or replace view ws_pressure_view as select time as starttime, baromabsin from ws_observations order by time asc;