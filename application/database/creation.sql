-- Database: tracking

CREATE DATABASE tracking;
COMMENT ON DATABASE tracking IS 'Undergraduate thesis project - Container tracking';

GRANT ALL ON DATABASE tracking TO postgres;
GRANT SELECT, INSERT, UPDATE, DELETE, CONNECT ON DATABASE tracking TO webapp;

-- Schema: tracking

CREATE SCHEMA tracking;
COMMENT ON SCHEMA tracking IS 'Schema for the Container Tracking application.';

