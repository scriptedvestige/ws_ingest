CREATE TABLE ws_observations (
    time TIMESTAMPTZ NOT NULL,
    baromabsin DOUBLE PRECISION,
    tempf REAL,
    humidity REAL,
    winddir INT,
    windspeedmph DOUBLE PRECISION,
    windgustmph DOUBLE PRECISION,
    maxdailygust DOUBLE PRECISION,
    solarradiation DOUBLE PRECISION,
    uv REAL,
    rainratein DOUBLE PRECISION,
    eventrainin DOUBLE PRECISION,
    PRIMARY KEY (time)
);