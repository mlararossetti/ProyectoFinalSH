DROP DATABASE IF EXISTS ProyectoFinalSH;
CREATE DATABASE ProyectoFinalSH;
USE ProyectoFinalSH;

-- Crear la tabla Años
CREATE TABLE anios (
    anio INT PRIMARY KEY
);

-- Tabla Calendario:
CREATE TABLE calendar (
    date DATE,
    dia INT,
    mes INT,
    trimestre INT,
    anio INT,
    dia_semana INT,
    PRIMARY KEY (date),
    UNIQUE (anio, mes),
	FOREIGN KEY (anio) REFERENCES anos(anios)
);

-- Tabla: merged_taxi_data
CREATE TABLE merged_taxi_data (
    date DATE NOT NULL,
    industry VARCHAR(50) NOT NULL,
    trips_per_day INT,
    farebox_per_day DECIMAL(10, 2),
    unique_drivers INT,
    unique_vehicles INT,
    vehicles_per_day INT,
    avg_days_vehicles_on_road DECIMAL(5, 2),
    avg_hours_per_day_per_vehicle DECIMAL(5, 2),
    avg_days_drivers_on_road DECIMAL(5, 2),
    avg_hours_per_day_per_driver DECIMAL(5, 2),
    percent_of_trips_paid_with_credit_card DECIMAL(3, 2),
    trips_per_day_shared INT,
    total_trips INT,
    passenger_count INT,
    avg_trip_distance DECIMAL(5, 2),
    avg_trip_duration DECIMAL(5, 2),
    total_amount INT,
    shared_match_flag INT,
    days_in_month INT,
    farebox_per_day_per_distance DECIMAL(10, 4),
    total_co2_emission DECIMAL(10, 4),
    
    PRIMARY KEY (date, industry),
    FOREIGN KEY (date) REFERENCES calendar(date)
);

-- Tabla: NY Boroughs
CREATE TABLE ny_boroughs (
    borough_id INT PRIMARY KEY,
    borough_name VARCHAR(50)
);

-- Tabla: NY Taxi Service Zone
CREATE TABLE ny_taxi_service_zone (
    service_zone_id INT PRIMARY KEY,
    service_zone_name VARCHAR(100)
);

-- Tabla: taxi_zone_lookup
CREATE TABLE taxi_zone_lookup (
    location_id INT PRIMARY KEY,
    zone VARCHAR(100),
    borough_id INT,
    service_zone_id INT,
    
	FOREIGN KEY (borough_id) REFERENCES ny_boroughs(borough_id),
    FOREIGN KEY (service_zone_id) REFERENCES ny_taxi_service_zone(service_zone_id)
);


-- Tabla: TLC Trip Record by Location
CREATE TABLE TLC_trip_record_by_location (
    date DATE,
    pickup_location_id INT NOT NULL,
    dropoff_location_id INT NOT NULL,
    total_trips INT,
    passenger_count INT,
    trip_distance DECIMAL(10, 2),
    trip_duration DECIMAL(10, 2),
    avg_trip_distance DECIMAL(5, 2),
    avg_trip_duration DECIMAL(5, 2),
    fare_amount INT,
    total_amount INT,
    shared_match_flag INT,
	
    PRIMARY KEY (date, pickup_location_id, dropoff_location_id),
    FOREIGN KEY (date) REFERENCES calendar(date),
    FOREIGN KEY (pickup_location_id) REFERENCES taxi_zone_lookup(location_id),
    FOREIGN KEY (dropoff_location_id) REFERENCES taxi_zone_lookup(location_id)
);


-- Tabla: Consolidados por Ciudad 18-23
CREATE TABLE consolidados_por_ciudad (
    year INT,
    code VARCHAR(10),
    city VARCHAR(100),
    days_with_aqi INT,
    good INT,
    moderate INT,
    unhealthy_t INT,
    very_unhealthy INT,
    hazardous INT,
    aqi_maximum INT,
    days_co INT,
    days_no2 INT,
    days_o3 INT,
    days_pm205 INT,
    days_pm10 INT,
    
	PRIMARY KEY (year, code),
	FOREIGN KEY (year) REFERENCES anos(anios)
);

-- Tabla: NY CO2 Emissions Inv
CREATE TABLE ny_co2_emissions_inv (
    inventory_type VARCHAR(50),
    sectors_sector VARCHAR(50),
    category_full VARCHAR(255),
    category_label VARCHAR(100),
    source_full VARCHAR(255),
    source_label VARCHAR(100),
    source_units VARCHAR(50),
    year INT,
    emission_tco2e DECIMAL(10, 2),
	PRIMARY KEY (year, inventory_type, sectors_sector, category_label),
    FOREIGN KEY (year) REFERENCES anos(anios)
);

-- Tabla: Electric Vehicles
CREATE TABLE electric_vehicles (
    brand VARCHAR(50),
    model VARCHAR(100),
    accelsec DECIMAL(5, 2),
    topSpeed_kmh DECIMAL(5, 2),
    range_km DECIMAL(5, 2),
    efficiency_whkm DECIMAL(5, 2),
    fastCharge_kmh DECIMAL(5, 2),
    rapid_charge VARCHAR(3),
    power_train VARCHAR(10),
    plug_type VARCHAR(20),
    body_style VARCHAR(20),
    segment VARCHAR(20),
    seats INT,
    price_euro DECIMAL(10, 2)
);


