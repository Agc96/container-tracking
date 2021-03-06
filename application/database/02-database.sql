-- Database: tracking
CREATE DATABASE tracking;
GRANT ALL ON DATABASE tracking TO postgres;
REVOKE ALL ON DATABASE tracking FROM scraper;
REVOKE ALL ON DATABASE tracking FROM predict;
REVOKE ALL ON DATABASE tracking FROM webapp;

-- OJO: Cambiar la base de datos actual de "postgres" a "tracking"
-- \c tracking

-- Schema: public
CREATE SCHEMA public;

-- Table: Carriers
CREATE TABLE tracking_enterprise (
    id serial NOT NULL PRIMARY KEY,
    name varchar(64) NOT NULL,
    carrier boolean NOT NULL DEFAULT TRUE,
    created_at timestamp with time zone NOT NULL DEFAULT NOW()
);

-- Table: Locations
CREATE TABLE tracking_location (
	id serial NOT NULL PRIMARY KEY,
	name varchar(128) NOT NULL,
	latitude double precision DEFAULT NULL,
	longitude double precision DEFAULT NULL,
    created_at timestamp with time zone NOT NULL DEFAULT NOW()
);

-- Table: Container Status
CREATE TABLE tracking_container_status (
    id serial NOT NULL PRIMARY KEY,
    name varchar(32) NOT NULL,
    created_at timestamp with time zone NOT NULL DEFAULT NOW()
);

-- Table: Containers
CREATE TABLE tracking_container (
    id serial NOT NULL PRIMARY KEY,
    code char(11) NOT NULL,
    carrier_id integer NOT NULL REFERENCES tracking_enterprise,
    origin_id integer DEFAULT NULL REFERENCES tracking_location,
    destination_id integer DEFAULT NULL REFERENCES tracking_location,
    arrival_date timestamp with time zone DEFAULT NULL,
    status_id integer NOT NULL DEFAULT 1 REFERENCES tracking_container_status,
    priority integer NOT NULL DEFAULT 1,
    created_at timestamp with time zone NOT NULL DEFAULT NOW()
);

-- Table: Vehicle
CREATE TABLE tracking_vehicle (
    id serial NOT NULL PRIMARY KEY,
    name varchar(32) NOT NULL,
    original_name varchar(32) NOT NULL,
    created_at timestamp with time zone NOT NULL DEFAULT NOW()
);

-- Table: Movement Status
CREATE TABLE tracking_movement_status (
    id serial NOT NULL PRIMARY KEY,
    status integer NOT NULL,
    name varchar(64) NOT NULL,
    enterprise_id integer NOT NULL REFERENCES tracking_enterprise,
    created_at timestamp with time zone NOT NULL DEFAULT NOW()
);

-- Table: Movement
CREATE TABLE tracking_movement (
    id serial NOT NULL PRIMARY KEY,
    container_id integer NOT NULL REFERENCES tracking_container,
    location_id integer NOT NULL REFERENCES tracking_location,
    status_id integer NOT NULL REFERENCES tracking_movement_status,
    date timestamp with time zone NOT NULL,
    vehicle_id integer DEFAULT NULL REFERENCES tracking_vehicle,
    vessel varchar(64) DEFAULT NULL,
    voyage varchar(32) DEFAULT NULL,
    estimated boolean NOT NULL,
    created_at timestamp with time zone NOT NULL DEFAULT NOW()
);

-- General permissions
GRANT CONNECT ON DATABASE tracking TO scraper;
GRANT CONNECT ON DATABASE tracking TO predict;
GRANT CONNECT ON DATABASE tracking TO webapp;

-- Permissions for the scraper
GRANT USAGE ON SCHEMA public TO scraper;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO scraper;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO scraper;

-- Permissions for the predictor
GRANT USAGE ON SCHEMA public TO predict;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO predict;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO predict;

-- Permissions for the webapp
GRANT USAGE ON SCHEMA public TO webapp;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO webapp;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO webapp;
