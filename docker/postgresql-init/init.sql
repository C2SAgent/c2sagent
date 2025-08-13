--
-- PostgreSQL database dump
--

-- Dumped from database version 16.9 (Ubuntu 16.9-0ubuntu0.24.04.1)
-- Dumped by pg_dump version 16.9 (Ubuntu 16.9-0ubuntu0.24.04.1)

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

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: agent_card; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.agent_card (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    description text,
    url character varying(255),
    version character varying(50),
    streaming boolean,
    examples jsonb,
    user_id integer NOT NULL,
    llm_name character varying(255),
    llm_url character varying(255),
    llm_key character varying(255)
);


ALTER TABLE public.agent_card OWNER TO postgres;

--
-- Name: agent_card_and_input_mode; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.agent_card_and_input_mode (
    id integer NOT NULL,
    agent_card_id integer NOT NULL,
    input_mode_id integer NOT NULL
);


ALTER TABLE public.agent_card_and_input_mode OWNER TO postgres;

--
-- Name: agent_card_and_input_mode_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.agent_card_and_input_mode_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.agent_card_and_input_mode_id_seq OWNER TO postgres;

--
-- Name: agent_card_and_input_mode_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.agent_card_and_input_mode_id_seq OWNED BY public.agent_card_and_input_mode.id;


--
-- Name: agent_card_and_mcp_server; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.agent_card_and_mcp_server (
    id integer NOT NULL,
    agent_card_id integer NOT NULL,
    mcp_server_id integer NOT NULL
);


ALTER TABLE public.agent_card_and_mcp_server OWNER TO postgres;

--
-- Name: agent_card_and_mcp_server_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.agent_card_and_mcp_server_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.agent_card_and_mcp_server_id_seq OWNER TO postgres;

--
-- Name: agent_card_and_mcp_server_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.agent_card_and_mcp_server_id_seq OWNED BY public.agent_card_and_mcp_server.id;


--
-- Name: agent_card_and_output_mode; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.agent_card_and_output_mode (
    id integer NOT NULL,
    agent_card_id integer NOT NULL,
    output_mode_id integer NOT NULL
);


ALTER TABLE public.agent_card_and_output_mode OWNER TO postgres;

--
-- Name: agent_card_and_output_mode_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.agent_card_and_output_mode_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.agent_card_and_output_mode_id_seq OWNER TO postgres;

--
-- Name: agent_card_and_output_mode_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.agent_card_and_output_mode_id_seq OWNED BY public.agent_card_and_output_mode.id;


--
-- Name: agent_card_and_skill; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.agent_card_and_skill (
    id integer NOT NULL,
    agent_card_id integer NOT NULL,
    skill_id integer NOT NULL
);


ALTER TABLE public.agent_card_and_skill OWNER TO postgres;

--
-- Name: agent_card_and_skill_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.agent_card_and_skill_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.agent_card_and_skill_id_seq OWNER TO postgres;

--
-- Name: agent_card_and_skill_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.agent_card_and_skill_id_seq OWNED BY public.agent_card_and_skill.id;


--
-- Name: agent_card_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.agent_card_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.agent_card_id_seq OWNER TO postgres;

--
-- Name: agent_card_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.agent_card_id_seq OWNED BY public.agent_card.id;


--
-- Name: data_sources; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.data_sources (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    description character varying(500),
    created_at timestamp without time zone DEFAULT '2025-07-16 22:45:59.663884'::timestamp without time zone,
    params jsonb
);


ALTER TABLE public.data_sources OWNER TO postgres;

--
-- Name: data_sources_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.data_sources_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.data_sources_id_seq OWNER TO postgres;

--
-- Name: data_sources_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.data_sources_id_seq OWNED BY public.data_sources.id;


--
-- Name: input_mode; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.input_mode (
    id integer NOT NULL,
    name character varying(255) NOT NULL
);


ALTER TABLE public.input_mode OWNER TO postgres;

--
-- Name: input_mode_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.input_mode_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.input_mode_id_seq OWNER TO postgres;

--
-- Name: input_mode_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.input_mode_id_seq OWNED BY public.input_mode.id;


--
-- Name: llm_config; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.llm_config (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    url character varying(255) NOT NULL,
    key character varying(255) NOT NULL,
    user_id integer NOT NULL
);


ALTER TABLE public.llm_config OWNER TO postgres;

--
-- Name: llm_config_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.llm_config_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.llm_config_id_seq OWNER TO postgres;

--
-- Name: llm_config_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.llm_config_id_seq OWNED BY public.llm_config.id;


--
-- Name: mcp_server; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.mcp_server (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    url character varying(255) NOT NULL,
    user_id integer NOT NULL
);


ALTER TABLE public.mcp_server OWNER TO postgres;

--
-- Name: mcp_server_and_tool; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.mcp_server_and_tool (
    id integer NOT NULL,
    mcp_server_id integer NOT NULL,
    tool_id integer NOT NULL
);


ALTER TABLE public.mcp_server_and_tool OWNER TO postgres;

--
-- Name: mcp_server_and_tool_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.mcp_server_and_tool_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.mcp_server_and_tool_id_seq OWNER TO postgres;

--
-- Name: mcp_server_and_tool_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.mcp_server_and_tool_id_seq OWNED BY public.mcp_server_and_tool.id;


--
-- Name: mcp_server_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.mcp_server_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.mcp_server_id_seq OWNER TO postgres;

--
-- Name: mcp_server_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.mcp_server_id_seq OWNED BY public.mcp_server.id;


--
-- Name: output_mode; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.output_mode (
    id integer NOT NULL,
    name character varying(255) NOT NULL
);


ALTER TABLE public.output_mode OWNER TO postgres;

--
-- Name: output_mode_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.output_mode_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.output_mode_id_seq OWNER TO postgres;

--
-- Name: output_mode_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.output_mode_id_seq OWNED BY public.output_mode.id;


--
-- Name: skill; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.skill (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    description text,
    tags jsonb,
    examples jsonb
);


ALTER TABLE public.skill OWNER TO postgres;

--
-- Name: skill_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.skill_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.skill_id_seq OWNER TO postgres;

--
-- Name: skill_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.skill_id_seq OWNED BY public.skill.id;


--
-- Name: time_series_data; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.time_series_data (
    id integer NOT NULL,
    data_source_id integer NOT NULL,
    "timestamp" timestamp without time zone NOT NULL,
    value double precision NOT NULL,
    created_at timestamp without time zone DEFAULT '2025-07-16 22:45:59.663884'::timestamp without time zone
);


ALTER TABLE public.time_series_data OWNER TO postgres;

--
-- Name: time_series_data_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.time_series_data_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.time_series_data_id_seq OWNER TO postgres;

--
-- Name: time_series_data_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.time_series_data_id_seq OWNED BY public.time_series_data.id;


--
-- Name: tool; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.tool (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    url character varying(255) NOT NULL
);


ALTER TABLE public.tool OWNER TO postgres;

--
-- Name: tool_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.tool_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.tool_id_seq OWNER TO postgres;

--
-- Name: tool_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.tool_id_seq OWNED BY public.tool.id;


--
-- Name: trained_models; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.trained_models (
    id integer NOT NULL,
    data_source_id integer NOT NULL,
    model_name character varying(100) NOT NULL,
    status character varying(20),
    params jsonb,
    metrics jsonb,
    created_at timestamp without time zone DEFAULT '2025-07-16 22:45:59.663884'::timestamp without time zone,
    updated_at timestamp without time zone DEFAULT '2025-07-16 22:45:59.663884'::timestamp without time zone
);


ALTER TABLE public.trained_models OWNER TO postgres;

--
-- Name: trained_models_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.trained_models_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.trained_models_id_seq OWNER TO postgres;

--
-- Name: trained_models_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.trained_models_id_seq OWNED BY public.trained_models.id;


--
-- Name: user_config; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.user_config (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    password character varying(255) NOT NULL,
    core_llm_name character varying(255),
    core_llm_url character varying(255),
    core_llm_key character varying(255)
);


ALTER TABLE public.user_config OWNER TO postgres;

--
-- Name: user_config_and_llm_config; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.user_config_and_llm_config (
    id integer NOT NULL,
    user_id integer NOT NULL,
    llm_id integer NOT NULL
);


ALTER TABLE public.user_config_and_llm_config OWNER TO postgres;

--
-- Name: user_config_and_llm_config_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.user_config_and_llm_config_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.user_config_and_llm_config_id_seq OWNER TO postgres;

--
-- Name: user_config_and_llm_config_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.user_config_and_llm_config_id_seq OWNED BY public.user_config_and_llm_config.id;


--
-- Name: user_config_and_media; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.user_config_and_media (
    id integer NOT NULL,
    name character varying(255),
    user_id integer NOT NULL,
    sessdata text,
    jct text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    cover_url character varying(255)
);


ALTER TABLE public.user_config_and_media OWNER TO postgres;

--
-- Name: user_config_and_media_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.user_config_and_media_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.user_config_and_media_id_seq OWNER TO postgres;

--
-- Name: user_config_and_media_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.user_config_and_media_id_seq OWNED BY public.user_config_and_media.id;


--
-- Name: user_config_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.user_config_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.user_config_id_seq OWNER TO postgres;

--
-- Name: user_config_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.user_config_id_seq OWNED BY public.user_config.id;


--
-- Name: agent_card id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.agent_card ALTER COLUMN id SET DEFAULT nextval('public.agent_card_id_seq'::regclass);


--
-- Name: agent_card_and_input_mode id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.agent_card_and_input_mode ALTER COLUMN id SET DEFAULT nextval('public.agent_card_and_input_mode_id_seq'::regclass);


--
-- Name: agent_card_and_mcp_server id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.agent_card_and_mcp_server ALTER COLUMN id SET DEFAULT nextval('public.agent_card_and_mcp_server_id_seq'::regclass);


--
-- Name: agent_card_and_output_mode id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.agent_card_and_output_mode ALTER COLUMN id SET DEFAULT nextval('public.agent_card_and_output_mode_id_seq'::regclass);


--
-- Name: agent_card_and_skill id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.agent_card_and_skill ALTER COLUMN id SET DEFAULT nextval('public.agent_card_and_skill_id_seq'::regclass);


--
-- Name: data_sources id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.data_sources ALTER COLUMN id SET DEFAULT nextval('public.data_sources_id_seq'::regclass);


--
-- Name: input_mode id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.input_mode ALTER COLUMN id SET DEFAULT nextval('public.input_mode_id_seq'::regclass);


--
-- Name: llm_config id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.llm_config ALTER COLUMN id SET DEFAULT nextval('public.llm_config_id_seq'::regclass);


--
-- Name: mcp_server id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.mcp_server ALTER COLUMN id SET DEFAULT nextval('public.mcp_server_id_seq'::regclass);


--
-- Name: mcp_server_and_tool id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.mcp_server_and_tool ALTER COLUMN id SET DEFAULT nextval('public.mcp_server_and_tool_id_seq'::regclass);


--
-- Name: output_mode id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.output_mode ALTER COLUMN id SET DEFAULT nextval('public.output_mode_id_seq'::regclass);


--
-- Name: skill id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.skill ALTER COLUMN id SET DEFAULT nextval('public.skill_id_seq'::regclass);


--
-- Name: time_series_data id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.time_series_data ALTER COLUMN id SET DEFAULT nextval('public.time_series_data_id_seq'::regclass);


--
-- Name: tool id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tool ALTER COLUMN id SET DEFAULT nextval('public.tool_id_seq'::regclass);


--
-- Name: trained_models id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.trained_models ALTER COLUMN id SET DEFAULT nextval('public.trained_models_id_seq'::regclass);


--
-- Name: user_config id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_config ALTER COLUMN id SET DEFAULT nextval('public.user_config_id_seq'::regclass);


--
-- Name: user_config_and_llm_config id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_config_and_llm_config ALTER COLUMN id SET DEFAULT nextval('public.user_config_and_llm_config_id_seq'::regclass);


--
-- Name: user_config_and_media id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_config_and_media ALTER COLUMN id SET DEFAULT nextval('public.user_config_and_media_id_seq'::regclass);


--
-- Name: agent_card_and_input_mode agent_card_and_input_mode_agent_card_id_input_mode_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.agent_card_and_input_mode
    ADD CONSTRAINT agent_card_and_input_mode_agent_card_id_input_mode_id_key UNIQUE (agent_card_id, input_mode_id);


--
-- Name: agent_card_and_input_mode agent_card_and_input_mode_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.agent_card_and_input_mode
    ADD CONSTRAINT agent_card_and_input_mode_pkey PRIMARY KEY (id);


--
-- Name: agent_card_and_mcp_server agent_card_and_mcp_server_agent_card_id_mcp_server_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.agent_card_and_mcp_server
    ADD CONSTRAINT agent_card_and_mcp_server_agent_card_id_mcp_server_id_key UNIQUE (agent_card_id, mcp_server_id);


--
-- Name: agent_card_and_mcp_server agent_card_and_mcp_server_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.agent_card_and_mcp_server
    ADD CONSTRAINT agent_card_and_mcp_server_pkey PRIMARY KEY (id);


--
-- Name: agent_card_and_output_mode agent_card_and_output_mode_agent_card_id_output_mode_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.agent_card_and_output_mode
    ADD CONSTRAINT agent_card_and_output_mode_agent_card_id_output_mode_id_key UNIQUE (agent_card_id, output_mode_id);


--
-- Name: agent_card_and_output_mode agent_card_and_output_mode_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.agent_card_and_output_mode
    ADD CONSTRAINT agent_card_and_output_mode_pkey PRIMARY KEY (id);


--
-- Name: agent_card_and_skill agent_card_and_skill_agent_card_id_skill_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.agent_card_and_skill
    ADD CONSTRAINT agent_card_and_skill_agent_card_id_skill_id_key UNIQUE (agent_card_id, skill_id);


--
-- Name: agent_card_and_skill agent_card_and_skill_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.agent_card_and_skill
    ADD CONSTRAINT agent_card_and_skill_pkey PRIMARY KEY (id);


--
-- Name: agent_card agent_card_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.agent_card
    ADD CONSTRAINT agent_card_pkey PRIMARY KEY (id);


--
-- Name: data_sources data_sources_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.data_sources
    ADD CONSTRAINT data_sources_pkey PRIMARY KEY (id);


--
-- Name: input_mode input_mode_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.input_mode
    ADD CONSTRAINT input_mode_pkey PRIMARY KEY (id);


--
-- Name: llm_config llm_config_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.llm_config
    ADD CONSTRAINT llm_config_pkey PRIMARY KEY (id);


--
-- Name: mcp_server_and_tool mcp_server_and_tool_mcp_server_id_tool_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.mcp_server_and_tool
    ADD CONSTRAINT mcp_server_and_tool_mcp_server_id_tool_id_key UNIQUE (mcp_server_id, tool_id);


--
-- Name: mcp_server_and_tool mcp_server_and_tool_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.mcp_server_and_tool
    ADD CONSTRAINT mcp_server_and_tool_pkey PRIMARY KEY (id);


--
-- Name: mcp_server mcp_server_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.mcp_server
    ADD CONSTRAINT mcp_server_pkey PRIMARY KEY (id);


--
-- Name: output_mode output_mode_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.output_mode
    ADD CONSTRAINT output_mode_pkey PRIMARY KEY (id);


--
-- Name: skill skill_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.skill
    ADD CONSTRAINT skill_pkey PRIMARY KEY (id);


--
-- Name: time_series_data time_series_data_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.time_series_data
    ADD CONSTRAINT time_series_data_pkey PRIMARY KEY (id);


--
-- Name: tool tool_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tool
    ADD CONSTRAINT tool_pkey PRIMARY KEY (id);


--
-- Name: trained_models trained_models_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.trained_models
    ADD CONSTRAINT trained_models_pkey PRIMARY KEY (id);


--
-- Name: user_config uq_user_config_name; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_config
    ADD CONSTRAINT uq_user_config_name UNIQUE (name);


--
-- Name: user_config_and_llm_config user_config_and_llm_config_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_config_and_llm_config
    ADD CONSTRAINT user_config_and_llm_config_pkey PRIMARY KEY (id);


--
-- Name: user_config_and_llm_config user_config_and_llm_config_user_id_llm_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_config_and_llm_config
    ADD CONSTRAINT user_config_and_llm_config_user_id_llm_id_key UNIQUE (user_id, llm_id);


--
-- Name: user_config_and_media user_config_and_media_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_config_and_media
    ADD CONSTRAINT user_config_and_media_pkey PRIMARY KEY (id);


--
-- Name: user_config user_config_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_config
    ADD CONSTRAINT user_config_pkey PRIMARY KEY (id);


--
-- Name: agent_card_and_input_mode agent_card_and_input_mode_agent_card_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.agent_card_and_input_mode
    ADD CONSTRAINT agent_card_and_input_mode_agent_card_id_fkey FOREIGN KEY (agent_card_id) REFERENCES public.agent_card(id) ON DELETE CASCADE;


--
-- Name: agent_card_and_input_mode agent_card_and_input_mode_input_mode_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.agent_card_and_input_mode
    ADD CONSTRAINT agent_card_and_input_mode_input_mode_id_fkey FOREIGN KEY (input_mode_id) REFERENCES public.input_mode(id) ON DELETE CASCADE;


--
-- Name: agent_card_and_mcp_server agent_card_and_mcp_server_agent_card_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.agent_card_and_mcp_server
    ADD CONSTRAINT agent_card_and_mcp_server_agent_card_id_fkey FOREIGN KEY (agent_card_id) REFERENCES public.agent_card(id) ON DELETE CASCADE;


--
-- Name: agent_card_and_mcp_server agent_card_and_mcp_server_mcp_server_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.agent_card_and_mcp_server
    ADD CONSTRAINT agent_card_and_mcp_server_mcp_server_id_fkey FOREIGN KEY (mcp_server_id) REFERENCES public.mcp_server(id) ON DELETE CASCADE;


--
-- Name: agent_card_and_output_mode agent_card_and_output_mode_agent_card_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.agent_card_and_output_mode
    ADD CONSTRAINT agent_card_and_output_mode_agent_card_id_fkey FOREIGN KEY (agent_card_id) REFERENCES public.agent_card(id) ON DELETE CASCADE;


--
-- Name: agent_card_and_output_mode agent_card_and_output_mode_output_mode_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.agent_card_and_output_mode
    ADD CONSTRAINT agent_card_and_output_mode_output_mode_id_fkey FOREIGN KEY (output_mode_id) REFERENCES public.output_mode(id) ON DELETE CASCADE;


--
-- Name: agent_card_and_skill agent_card_and_skill_agent_card_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.agent_card_and_skill
    ADD CONSTRAINT agent_card_and_skill_agent_card_id_fkey FOREIGN KEY (agent_card_id) REFERENCES public.agent_card(id) ON DELETE CASCADE;


--
-- Name: agent_card_and_skill agent_card_and_skill_skill_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.agent_card_and_skill
    ADD CONSTRAINT agent_card_and_skill_skill_id_fkey FOREIGN KEY (skill_id) REFERENCES public.skill(id) ON DELETE CASCADE;


--
-- Name: agent_card agent_card_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.agent_card
    ADD CONSTRAINT agent_card_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.user_config(id) ON DELETE CASCADE;


--
-- Name: llm_config fk_llm_config_user_config; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.llm_config
    ADD CONSTRAINT fk_llm_config_user_config FOREIGN KEY (user_id) REFERENCES public.user_config(id) ON DELETE CASCADE;


--
-- Name: mcp_server fk_mcp_server_user_config; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.mcp_server
    ADD CONSTRAINT fk_mcp_server_user_config FOREIGN KEY (user_id) REFERENCES public.user_config(id) ON DELETE CASCADE;


--
-- Name: user_config_and_media fk_user_config; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_config_and_media
    ADD CONSTRAINT fk_user_config FOREIGN KEY (user_id) REFERENCES public.user_config(id) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: mcp_server_and_tool mcp_server_and_tool_mcp_server_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.mcp_server_and_tool
    ADD CONSTRAINT mcp_server_and_tool_mcp_server_id_fkey FOREIGN KEY (mcp_server_id) REFERENCES public.mcp_server(id) ON DELETE CASCADE;


--
-- Name: mcp_server_and_tool mcp_server_and_tool_tool_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.mcp_server_and_tool
    ADD CONSTRAINT mcp_server_and_tool_tool_id_fkey FOREIGN KEY (tool_id) REFERENCES public.tool(id) ON DELETE CASCADE;


--
-- Name: time_series_data time_series_data_data_source_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.time_series_data
    ADD CONSTRAINT time_series_data_data_source_id_fkey FOREIGN KEY (data_source_id) REFERENCES public.data_sources(id);


--
-- Name: trained_models trained_models_data_source_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.trained_models
    ADD CONSTRAINT trained_models_data_source_id_fkey FOREIGN KEY (data_source_id) REFERENCES public.data_sources(id);


--
-- Name: user_config_and_llm_config user_config_and_llm_config_llm_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_config_and_llm_config
    ADD CONSTRAINT user_config_and_llm_config_llm_id_fkey FOREIGN KEY (llm_id) REFERENCES public.llm_config(id) ON DELETE CASCADE;


--
-- Name: user_config_and_llm_config user_config_and_llm_config_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_config_and_llm_config
    ADD CONSTRAINT user_config_and_llm_config_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.user_config(id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--
