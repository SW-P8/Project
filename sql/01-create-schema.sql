CREATE TABLE TaxiData (
    taxi_id INTEGER NOT NULL,
    date_time TIMESTAMP NOT NULL,
    longitude FLOAT NOT NULL,
    latitude FLOAT NOT NULL,
    trajectory_id INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS DTC_model_min_coords (
    model_id SERIAL PRIMARY KEY,
    min_longitude FLOAT NOT NULL,
    min_latitude FLOAT NOT NULL
);

CREATE TABLE IF NOT EXISTS DTC_model_safe_areas (
    area_id SERIAL PRIMARY KEY,
    model_id INT NOT NULL,
    anchor_x FLOAT NOT NULL,
    anchor_y FLOAT NOT NULL,
    radius FLOAT NOT NULL,
    FOREIGN KEY (model_id) REFERENCES DTC_model_min_coords(model_id) ON DELETE CASCADE
);