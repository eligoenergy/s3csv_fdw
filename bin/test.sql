--
-- PostgreSQL database dump
--

SET statement_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

--
-- Name: dyn; Type: DATABASE; Schema: -; Owner: fabio
--


DROP DATABASE dyn;
CREATE DATABASE dyn WITH TEMPLATE = template0 ENCODING = 'UTF8' LC_COLLATE = 'es_ES.UTF-8' LC_CTYPE = 'es_ES.UTF-8';


ALTER DATABASE dyn OWNER TO fabio;

\connect dyn

SET statement_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

--
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;


--
-- Name: EXTENSION plpgsql; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';


--
-- Name: multicorn; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS multicorn WITH SCHEMA public;


--
-- Name: EXTENSION multicorn; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION multicorn IS 'Multicorn Python bindings for Postgres 9.1.* Foreign Data Wrapper';


--
-- Name: public; Type: ACL; Schema: -; Owner: postgres
--

REVOKE ALL ON SCHEMA public FROM PUBLIC;
REVOKE ALL ON SCHEMA public FROM postgres;
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO PUBLIC;


--
-- PostgreSQL database dump complete
--

CREATE SERVER multicorn_dynamo FOREIGN DATA WRAPPER multicorn
options (
		  wrapper 'multicorn.dynamodbfdw.DynamoFdw'
	);


CREATE FOREIGN TABLE test (
		id_pk  character varying,
		newfield  integer
	) server multicorn_dynamo options(
	aws_region  'eu-west-1',
	remote_table 'test'
);

CREATE USER MAPPING FOR fabio SERVER multicorn_dynamo OPTIONS (aws_access_key_id  'XXXXXXXXXXXXXXXX',aws_secret_access_key  'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX');


SELECT * from test;
