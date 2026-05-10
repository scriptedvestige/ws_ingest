CREATE TABLE rain_totals (
    time TIMESTAMPTZ NOT NULL,
    hourlyrainin DOUBLE PRECISION,
    dailyrainin DOUBLE PRECISION,
    weeklyrainin DOUBLE PRECISION,
    monthlyrainin DOUBLE PRECISION,
    yearlyrainin DOUBLE PRECISION,
    PRIMARY KEY (time)
);



CREATE TABLE rain_totals (time TIMESTAMPTZ NOT NULL, hourlyrainin DOUBLE PRECISION, dailyrainin DOUBLE PRECISION, weeklyrainin DOUBLE PRECISION, monthlyrainin DOUBLE PRECISION, yearlyrainin DOUBLE PRECISION, PRIMARY KEY (time));