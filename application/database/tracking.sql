--
-- PostgreSQL database dump
--

-- Dumped from database version 10.8
-- Dumped by pg_dump version 10.8

-- Started on 2019-05-21 22:38:08

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- TOC entry 2825 (class 0 OID 0)
-- Dependencies: 2824
-- Name: DATABASE tracking; Type: COMMENT; Schema: -; Owner: postgres
--

COMMENT ON DATABASE tracking IS 'Undergraduate thesis project - Container tracking';


--
-- TOC entry 5 (class 2615 OID 16394)
-- Name: tracking; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA tracking;


ALTER SCHEMA tracking OWNER TO postgres;

--
-- TOC entry 2827 (class 0 OID 0)
-- Dependencies: 5
-- Name: SCHEMA tracking; Type: COMMENT; Schema: -; Owner: postgres
--

COMMENT ON SCHEMA tracking IS 'Schema for the Container Tracking application.';


--
-- TOC entry 1 (class 3079 OID 12924)
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;


--
-- TOC entry 2828 (class 0 OID 0)
-- Dependencies: 1
-- Name: EXTENSION plpgsql; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';


SET default_tablespace = '';

SET default_with_oids = false;

--
-- TOC entry 202 (class 1259 OID 16416)
-- Name: carriers; Type: TABLE; Schema: tracking; Owner: postgres
--

CREATE TABLE tracking.carriers (
    carrier_id integer NOT NULL,
    carrier_name character varying(64) NOT NULL
);


ALTER TABLE tracking.carriers OWNER TO postgres;

--
-- TOC entry 2829 (class 0 OID 0)
-- Dependencies: 202
-- Name: TABLE carriers; Type: COMMENT; Schema: tracking; Owner: postgres
--

COMMENT ON TABLE tracking.carriers IS 'List of container shipping carriers for the Container Tracking application.';


--
-- TOC entry 201 (class 1259 OID 16414)
-- Name: carriers_carrier_id_seq; Type: SEQUENCE; Schema: tracking; Owner: postgres
--

CREATE SEQUENCE tracking.carriers_carrier_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE tracking.carriers_carrier_id_seq OWNER TO postgres;

--
-- TOC entry 2830 (class 0 OID 0)
-- Dependencies: 201
-- Name: carriers_carrier_id_seq; Type: SEQUENCE OWNED BY; Schema: tracking; Owner: postgres
--

ALTER SEQUENCE tracking.carriers_carrier_id_seq OWNED BY tracking.carriers.carrier_id;


--
-- TOC entry 200 (class 1259 OID 16408)
-- Name: containers; Type: TABLE; Schema: tracking; Owner: postgres
--

CREATE TABLE tracking.containers (
    container_id integer NOT NULL,
    container_code character(11) NOT NULL,
    carrier_id integer NOT NULL
);


ALTER TABLE tracking.containers OWNER TO postgres;

--
-- TOC entry 2831 (class 0 OID 0)
-- Dependencies: 200
-- Name: TABLE containers; Type: COMMENT; Schema: tracking; Owner: postgres
--

COMMENT ON TABLE tracking.containers IS 'List of intermodal containers for the Container Tracking application.';


--
-- TOC entry 199 (class 1259 OID 16406)
-- Name: containers_container_id_seq; Type: SEQUENCE; Schema: tracking; Owner: postgres
--

CREATE SEQUENCE tracking.containers_container_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE tracking.containers_container_id_seq OWNER TO postgres;

--
-- TOC entry 2832 (class 0 OID 0)
-- Dependencies: 199
-- Name: containers_container_id_seq; Type: SEQUENCE OWNED BY; Schema: tracking; Owner: postgres
--

ALTER SEQUENCE tracking.containers_container_id_seq OWNED BY tracking.containers.container_id;


--
-- TOC entry 198 (class 1259 OID 16400)
-- Name: users; Type: TABLE; Schema: tracking; Owner: postgres
--

CREATE TABLE tracking.users (
    user_id integer NOT NULL,
    fullname character varying(64) NOT NULL,
    email character varying(64) NOT NULL,
    username character varying(32) NOT NULL,
    password character varying(128) NOT NULL
);


ALTER TABLE tracking.users OWNER TO postgres;

--
-- TOC entry 2833 (class 0 OID 0)
-- Dependencies: 198
-- Name: TABLE users; Type: COMMENT; Schema: tracking; Owner: postgres
--

COMMENT ON TABLE tracking.users IS 'List of users for the Container Tracking application.';


--
-- TOC entry 197 (class 1259 OID 16398)
-- Name: users_user_id_seq; Type: SEQUENCE; Schema: tracking; Owner: postgres
--

CREATE SEQUENCE tracking.users_user_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE tracking.users_user_id_seq OWNER TO postgres;

--
-- TOC entry 2834 (class 0 OID 0)
-- Dependencies: 197
-- Name: users_user_id_seq; Type: SEQUENCE OWNED BY; Schema: tracking; Owner: postgres
--

ALTER SEQUENCE tracking.users_user_id_seq OWNED BY tracking.users.user_id;


--
-- TOC entry 2685 (class 2604 OID 16419)
-- Name: carriers carrier_id; Type: DEFAULT; Schema: tracking; Owner: postgres
--

ALTER TABLE ONLY tracking.carriers ALTER COLUMN carrier_id SET DEFAULT nextval('tracking.carriers_carrier_id_seq'::regclass);


--
-- TOC entry 2684 (class 2604 OID 16411)
-- Name: containers container_id; Type: DEFAULT; Schema: tracking; Owner: postgres
--

ALTER TABLE ONLY tracking.containers ALTER COLUMN container_id SET DEFAULT nextval('tracking.containers_container_id_seq'::regclass);


--
-- TOC entry 2683 (class 2604 OID 16403)
-- Name: users user_id; Type: DEFAULT; Schema: tracking; Owner: postgres
--

ALTER TABLE ONLY tracking.users ALTER COLUMN user_id SET DEFAULT nextval('tracking.users_user_id_seq'::regclass);


--
-- TOC entry 2818 (class 0 OID 16416)
-- Dependencies: 202
-- Data for Name: carriers; Type: TABLE DATA; Schema: tracking; Owner: postgres
--

COPY tracking.carriers (carrier_id, carrier_name) FROM stdin;
\.


--
-- TOC entry 2816 (class 0 OID 16408)
-- Dependencies: 200
-- Data for Name: containers; Type: TABLE DATA; Schema: tracking; Owner: postgres
--

COPY tracking.containers (container_id, container_code, carrier_id) FROM stdin;
\.


--
-- TOC entry 2814 (class 0 OID 16400)
-- Dependencies: 198
-- Data for Name: users; Type: TABLE DATA; Schema: tracking; Owner: postgres
--

COPY tracking.users (user_id, fullname, email, username, password) FROM stdin;
\.


--
-- TOC entry 2835 (class 0 OID 0)
-- Dependencies: 201
-- Name: carriers_carrier_id_seq; Type: SEQUENCE SET; Schema: tracking; Owner: postgres
--

SELECT pg_catalog.setval('tracking.carriers_carrier_id_seq', 1, false);


--
-- TOC entry 2836 (class 0 OID 0)
-- Dependencies: 199
-- Name: containers_container_id_seq; Type: SEQUENCE SET; Schema: tracking; Owner: postgres
--

SELECT pg_catalog.setval('tracking.containers_container_id_seq', 1, false);


--
-- TOC entry 2837 (class 0 OID 0)
-- Dependencies: 197
-- Name: users_user_id_seq; Type: SEQUENCE SET; Schema: tracking; Owner: postgres
--

SELECT pg_catalog.setval('tracking.users_user_id_seq', 1, false);


--
-- TOC entry 2691 (class 2606 OID 16421)
-- Name: carriers carriers_pkey; Type: CONSTRAINT; Schema: tracking; Owner: postgres
--

ALTER TABLE ONLY tracking.carriers
    ADD CONSTRAINT carriers_pkey PRIMARY KEY (carrier_id);


--
-- TOC entry 2689 (class 2606 OID 16413)
-- Name: containers containers_pkey; Type: CONSTRAINT; Schema: tracking; Owner: postgres
--

ALTER TABLE ONLY tracking.containers
    ADD CONSTRAINT containers_pkey PRIMARY KEY (container_id);


--
-- TOC entry 2687 (class 2606 OID 16405)
-- Name: users users_pkey; Type: CONSTRAINT; Schema: tracking; Owner: postgres
--

ALTER TABLE ONLY tracking.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (user_id);


-- Completed on 2019-05-21 22:38:08

--
-- PostgreSQL database dump complete
--

