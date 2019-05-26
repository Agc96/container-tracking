-- Database: tracking

CREATE DATABASE tracking;
COMMENT ON DATABASE tracking IS 'Undergraduate thesis project - Container tracking';

GRANT ALL ON DATABASE tracking TO postgres;
GRANT CONNECT ON DATABASE tracking TO webapp;

-- Schema: tracking

DROP SCHEMA public CASCADE;
CREATE SCHEMA public;
COMMENT ON SCHEMA public IS 'Schema for the Container Tracking application.';

-- Table: Users

CREATE TABLE tracking_users (
    id serial NOT NULL PRIMARY KEY,
    fullname varchar(64) NOT NULL,
    email varchar(64) NOT NULL,
    role integer NOT NULL,
    username varchar(32) NOT NULL,
    password varchar(128) NOT NULL
);
COMMENT ON TABLE tracking_users IS 'List of users for the Container Tracking application.';
COMMENT ON COLUMN tracking_users.id IS 'ID of the user.';
COMMENT ON COLUMN tracking_users.fullname IS 'First and last name of the user.';
COMMENT ON COLUMN tracking_users.email IS 'Email of the user.';
COMMENT ON COLUMN tracking_users.role IS 'Role of the user.\n1: Administrator\n2: Logistic area user\n3: Systems area user';
COMMENT ON COLUMN tracking_users.username IS 'Short name used by the user to login.';
COMMENT ON COLUMN tracking_users.password IS 'Encrypted bassword used by the user to login.';

-- Table: Carriers

CREATE TABLE tracking_carriers (
    id serial NOT NULL PRIMARY KEY,
    name varchar(64) NOT NULL
);
COMMENT ON TABLE tracking_carriers IS 'List of container shipping carriers for the Container Tracking application.';
COMMENT ON COLUMN tracking_carriers.id IS 'ID of the carrier.';
COMMENT ON COLUMN tracking_carriers.name IS 'Name of the carrier.';

-- Table: Locations

CREATE TABLE tracking_locations (
	id serial NOT NULL PRIMARY KEY,
	name varchar(64) NOT NULL,
	latitude double precision NOT NULL,
	longitude double precision NOT NULL
);
COMMENT ON TABLE tracking_locations IS 'List of saved locations for both the Container Tracking web scraper and the Container Tracking application.';
COMMENT ON COLUMN tracking_locations.id IS 'ID of the location.';
COMMENT ON COLUMN tracking_locations.name IS 'Name of the location.';
COMMENT ON COLUMN tracking_locations.latitude IS 'Latitude of the location. Valid range is [-90.0, 90.0]';
COMMENT ON COLUMN tracking_locations.longitude IS 'Longitude of the location. Valid range is [-180.0, 180.0]';

-- Table: Containers

CREATE TABLE tracking_containers (
    id serial NOT NULL PRIMARY KEY,
    code char(11) NOT NULL,
    carrier_id integer NOT NULL REFERENCES tracking_carriers,
    origin_id integer NOT NULL REFERENCES tracking_locations,
    destination_id integer NOT NULL REFERENCES tracking_locations,
    processed boolean NOT NULL DEFAULT FALSE,
    arrival_date timestamp DEFAULT NULL
);
COMMENT ON TABLE tracking_containers IS 'List of intermodal containers for the Container Tracking application.';
COMMENT ON COLUMN tracking_containers.id IS 'ID of the container.';
COMMENT ON COLUMN tracking_containers.code IS 'Standardized code of the container. Contains 4 letters + 6 digits + verification digit.';
COMMENT ON COLUMN tracking_containers.carrier_id IS 'ID of the carrier that transports the container.';
COMMENT ON COLUMN tracking_containers.origin_id IS 'ID of the origin port location of the container.';
COMMENT ON COLUMN tracking_containers.destination_id IS 'ID of the destination port location of the container.';
COMMENT ON COLUMN tracking_containers.processed IS 'Shows if the container was processed by the web scraper.';
COMMENT ON COLUMN tracking_containers.arrival_date IS 'Estimated arrival date and time of the container, based on the machine learning predictor.';

-- Permissions for the Web application

GRANT USAGE ON SCHEMA public TO webapp;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO webapp;
GRANT INSERT ON ALL TABLES IN SCHEMA public TO webapp;
GRANT UPDATE ON ALL TABLES IN SCHEMA public TO webapp;
GRANT DELETE ON ALL TABLES IN SCHEMA public TO webapp;
