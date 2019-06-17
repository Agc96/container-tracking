-- Database: tracking

CREATE DATABASE tracking;
COMMENT ON DATABASE tracking IS 'Undergraduate thesis project - Container tracking';

GRANT ALL ON DATABASE tracking TO postgres;
GRANT ALL ON DATABASE tracking TO webmaster;
GRANT CONNECT ON DATABASE tracking TO webapp;

-- Schema: tracking
-- OJO: Cambiar la base de datos actual de "postgres" a "tracking" (\c tracking)

COMMENT ON SCHEMA public IS 'Schema for the Container Tracking application.';

-- Table: Carriers

CREATE TABLE tracking_carrier (
    id serial NOT NULL PRIMARY KEY,
    name varchar(64) NOT NULL
);
COMMENT ON TABLE tracking_carrier IS 'List of container shipping carriers for the Container Tracking application.';
COMMENT ON COLUMN tracking_carrier.id IS 'ID of the carrier.';
COMMENT ON COLUMN tracking_carrier.name IS 'Name of the carrier.';

-- Table: Locations

CREATE TABLE tracking_location (
	id serial NOT NULL PRIMARY KEY,
	name varchar(128) NOT NULL,
	latitude double precision NOT NULL,
	longitude double precision NOT NULL
);
COMMENT ON TABLE tracking_location IS 'List of saved locations for both the Container Tracking web scraper and the Container Tracking application.';
COMMENT ON COLUMN tracking_location.id IS 'ID of the location.';
COMMENT ON COLUMN tracking_location.name IS 'Name of the location.';
COMMENT ON COLUMN tracking_location.latitude IS 'Latitude of the location. Valid range is [-90.0, 90.0]';
COMMENT ON COLUMN tracking_location.longitude IS 'Longitude of the location. Valid range is [-180.0, 180.0]';

-- Table: Containers

CREATE TABLE tracking_container (
    id serial NOT NULL PRIMARY KEY,
    code char(11) NOT NULL,
    carrier_id integer NOT NULL REFERENCES tracking_carrier,
    origin_id integer NOT NULL REFERENCES tracking_location,
    destination_id integer NOT NULL REFERENCES tracking_location,
    processed boolean NOT NULL DEFAULT FALSE,
    arrival_date timestamp with time zone DEFAULT NULL,
    created_at timestamp with time zone DEFAULT now()
);
COMMENT ON TABLE tracking_container IS 'List of intermodal containers for the Container Tracking application.';
COMMENT ON COLUMN tracking_container.id IS 'ID of the container.';
COMMENT ON COLUMN tracking_container.code IS 'Standardized code of the container. Contains 4 letters + 6 digits + verification digit.';
COMMENT ON COLUMN tracking_container.carrier_id IS 'ID of the carrier that transports the container.';
COMMENT ON COLUMN tracking_container.origin_id IS 'ID of the origin port location of the container.';
COMMENT ON COLUMN tracking_container.destination_id IS 'ID of the destination port location of the container.';
COMMENT ON COLUMN tracking_container.processed IS 'Shows if the container was processed by the web scraper.';
COMMENT ON COLUMN tracking_container.arrival_date IS 'Estimated arrival date and time of the container, based on the machine learning predictor.';

-- Permissions for the Web application

GRANT USAGE ON SCHEMA public TO webapp;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO webapp;
GRANT INSERT ON ALL TABLES IN SCHEMA public TO webapp;
GRANT UPDATE ON ALL TABLES IN SCHEMA public TO webapp;
GRANT DELETE ON ALL TABLES IN SCHEMA public TO webapp;

GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO webapp;

GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO webmaster;
