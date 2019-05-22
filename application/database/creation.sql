-- Database: tracking

CREATE DATABASE tracking;
COMMENT ON DATABASE tracking IS 'Undergraduate thesis project - Container tracking';

-- GRANT ALL ON DATABASE tracking TO postgres;
GRANT CONNECT ON DATABASE tracking TO webapp;

-- Schema: tracking

CREATE SCHEMA tracking;
COMMENT ON SCHEMA tracking IS 'Schema for the Container Tracking application.';

GRANT USAGE ON SCHEMA tracking TO webapp;
GRANT SELECT ON ALL TABLES IN SCHEMA tracking TO webapp;
GRANT INSERT ON ALL TABLES IN SCHEMA tracking TO webapp;
GRANT UPDATE ON ALL TABLES IN SCHEMA tracking TO webapp;
GRANT DELETE ON ALL TABLES IN SCHEMA tracking TO webapp;

-- Table: Users

CREATE TABLE tracking.users (
    user_id serial PRIMARY KEY,
    fullname varchar(64) NOT NULL,
    email varchar(64) NOT NULL,
    role integer NOT NULL,
    username varchar(32) NOT NULL,
    password varchar(64) NOT NULL
);
COMMENT ON TABLE tracking.locations IS 'List of users for the Container Tracking application.';

-- Table: Carriers

CREATE TABLE tracking.carriers (
    carrier_id serial PRIMARY KEY,
    name varchar(64) NOT NULL
);
COMMENT ON TABLE tracking.carriers IS 'List of container shipping carriers for the Container Tracking application.';

-- Table: Locations

CREATE TABLE tracking.locations (
	location_id serial PRIMARY KEY,
	name varchar(64) NOT NULL,
	latitude double precision NOT NULL,
	longitude double precision NOT NULL
);
COMMENT ON TABLE tracking.locations IS 'TODO';

-- Table: Containers

CREATE TABLE tracking.containers (
    container_id SERIAL PRIMARY KEY,
    code CHAR(11) NOT NULL,
    carrier_id INTEGER NOT NULL REFERENCES carriers.carrier_id,
    origin_id INTEGER NOT NULL REFERENCES locations.location_id
);
COMMENT ON TABLE tracking.containers IS 'TODO';
