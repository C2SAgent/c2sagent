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
-- Name: tool id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tool ALTER COLUMN id SET DEFAULT nextval('public.tool_id_seq'::regclass);


--
-- Name: user_config id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_config ALTER COLUMN id SET DEFAULT nextval('public.user_config_id_seq'::regclass);


--
-- Name: user_config_and_llm_config id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_config_and_llm_config ALTER COLUMN id SET DEFAULT nextval('public.user_config_and_llm_config_id_seq'::regclass);


--
-- Data for Name: agent_card; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.agent_card (id, name, description, url, version, streaming, examples, user_id, llm_name, llm_url, llm_key) FROM stdin;
3	q		\N	1.0	f	[]	35	gpt-4		
4	e	e	\N	1.0	f	[]	35	e	e	e
5	y	y	\N	1.0	f	[]	35	gpt-4		
6	n		\N	1.0	f	[]	35	gpt-4		
7	q		\N	1.0	f	[]	35	gpt-4		
8	生活	用来回答生活问题的	\N	1.0	f	[]	36	deepseek	https://api.deepseek.com/v1	sk-7f49c72dbe9a4284b156701b84aa42a8
\.


--
-- Data for Name: agent_card_and_input_mode; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.agent_card_and_input_mode (id, agent_card_id, input_mode_id) FROM stdin;
\.


--
-- Data for Name: agent_card_and_mcp_server; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.agent_card_and_mcp_server (id, agent_card_id, mcp_server_id) FROM stdin;
4	8	3
\.


--
-- Data for Name: agent_card_and_output_mode; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.agent_card_and_output_mode (id, agent_card_id, output_mode_id) FROM stdin;
\.


--
-- Data for Name: agent_card_and_skill; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.agent_card_and_skill (id, agent_card_id, skill_id) FROM stdin;
\.


--
-- Data for Name: input_mode; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.input_mode (id, name) FROM stdin;
\.


--
-- Data for Name: llm_config; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.llm_config (id, name, url, key, user_id) FROM stdin;
\.


--
-- Data for Name: mcp_server; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.mcp_server (id, name, url, user_id) FROM stdin;
3	t		36
\.


--
-- Data for Name: mcp_server_and_tool; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.mcp_server_and_tool (id, mcp_server_id, tool_id) FROM stdin;
\.


--
-- Data for Name: output_mode; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.output_mode (id, name) FROM stdin;
\.


--
-- Data for Name: skill; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.skill (id, name, description, tags, examples) FROM stdin;
1	new_skill	默认描述	\N	\N
\.


--
-- Data for Name: tool; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.tool (id, name, url) FROM stdin;
\.


--
-- Data for Name: user_config; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.user_config (id, name, password, core_llm_name, core_llm_url, core_llm_key) FROM stdin;
1	newuser	hashed_password	gpt-4	\N	\N
11	test_user	hashed_password	deepseek	https://api.deepseek.com/v1	sk-fc9e70085fe4411fb5b3f5aa121ee9a9
12	super_admin	super_admin	deepseek	https://api.deepseek.com/v1	sk-fc9e70085fe4411fb5b3f5aa121ee9a9
14	test01	$2b$12$zc.rkTSHralEW8Nvhrk3YuM4i6FgqovD4VzNtQYHhGSqicNIAv8Eq	\N	\N	\N
15	testuser	$2b$12$sDNmQh2r5o59R69d3.ysTONvblzT0pC2F.i1ggLxYmg2JJvsqc1qq	default	http://example.com	12345
16	test02	$2b$12$ToeOJ5XkhLS.farRFjSY.uCAw/iiHcPnMLCyi6A6NPtAk3UQNyYqi	default	http://example.com	12345
17	test03	$2b$12$KHsWrv7zKsKHcyIE8llL3.nw3vV98woefm3px1A6wtnF6dUFe6w1a	default	http://example.com	12345
18	test04	$2b$12$hOsX9VZdJCw1s16swFMSHOIYN0HqVCRW0ppnCDuY5At7cWsx7E75K	default	http://example.com	12345
19	test05	$2b$12$QwfZG.BKJBgOC069fWXawu.qzEJJHMX/L2JwQ4C2JGPCo0QGZl.sa	default	http://example.com	12345
20	test06	$2b$12$CAM3n4Yh.8gSDPhWFOmLyeylDROrxDjausqqyUps.VdkSgPfSZXtm	default	http://example.com	12345
21	test07	$2b$12$Uzm3awnbrQSOO2PN5VMlaeLSCSCVEruBAF4625a15n1Q2e.uczJzS	default	http://example.com	12345
22	test11	$2b$12$YD3ULeV/hHdn.eT3n4BijuLMPZpTjIvTv8.pTmzrkoQsHgCr0dUsO			
23	test12	$2b$12$TbJHmw1CUhUFyTlBRzhqTuPdzBbek4rgDBoM.9wla5JxwQFweGtT.			
24	test13	$2b$12$oxvQUwyTNIdivN4f4idLIO6IB.PhTcACjWhrPxdKPPa74Jcccfkfq			
25	test15	$2b$12$BPRNqIMaLDMPpzEuvbngPeTpTdpCWmo4Zg5L.ws/i0cZbH/QQZzyG			
26	tttt	$2b$12$xcOoVWwmOt5mstC7HGh1AuVu1Jta3R3ymz2maUXw3qAMJufTGP5iS			
27	test16	$2b$12$jO7GYjWzq8Ki3ivxjCtqp.Uv.zNZ6zg8jWwvIBm6r1lKKbXgPHzH6			
28	test17	$2b$12$zsy8a3xNP4/FOtra7G/YAunicSu/YOn1hhDZPiJebIiG89IqXjVCm			
29	ttttt	$2b$12$d39e0KVNRV9ciY87PqOjl.fUZYdi/WWpayaBGFscJwcWlZk4N0Ify			
30	test55	$2b$12$jngexk/pk1ukubgJOwe2xeJoJgAzNIDbYe4jZ0Zz0UOJ0d.SfBa2W			
31	test22	$2b$12$U9qpWWo1m9nK9X8m2tkZeOrB.obXT.uWXDG1.vqfn0JvYcVFVbE.2			
32	test88	$2b$12$CKXMczM3Iqvup1fyOCiove/ZyJzgms.yJKn9sNFs65huwpKv8ji6m	default	http://example.com	12345
33	admin	$2b$12$rd5SMdowEamtJz6Pl/x4t.YxOw0Befe7EF0CdwHlEUwgQjA7IiRiW			
34	myuser	$2b$12$hsmGr1uloemvAMc74x7LKethTPcAcvIShXPy7LKykh7dnclGhmlFK			
35	ttt	$2b$12$elxF35Eh0X3W8jXOUteDduPd6mQYztZ59lZ2k54oWgfKJei.2rWwu			
36	agent	$2b$12$y0UZhryJkJunw5FPn4dpseQxOI4ZIP/EgCgklxLFi1s0TpYDXid9C	deepseek	https://api.deepseek.com/v1	sk-7f49c72dbe9a4284b156701b84aa42a8
\.


--
-- Data for Name: user_config_and_llm_config; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.user_config_and_llm_config (id, user_id, llm_id) FROM stdin;
\.


--
-- Name: agent_card_and_input_mode_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.agent_card_and_input_mode_id_seq', 1, false);


--
-- Name: agent_card_and_mcp_server_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.agent_card_and_mcp_server_id_seq', 4, true);


--
-- Name: agent_card_and_output_mode_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.agent_card_and_output_mode_id_seq', 1, false);


--
-- Name: agent_card_and_skill_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.agent_card_and_skill_id_seq', 1, false);


--
-- Name: agent_card_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.agent_card_id_seq', 9, true);


--
-- Name: input_mode_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.input_mode_id_seq', 1, false);


--
-- Name: llm_config_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.llm_config_id_seq', 1, false);


--
-- Name: mcp_server_and_tool_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.mcp_server_and_tool_id_seq', 1, false);


--
-- Name: mcp_server_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.mcp_server_id_seq', 3, true);


--
-- Name: output_mode_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.output_mode_id_seq', 1, false);


--
-- Name: skill_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.skill_id_seq', 1, true);


--
-- Name: tool_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.tool_id_seq', 1, false);


--
-- Name: user_config_and_llm_config_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.user_config_and_llm_config_id_seq', 1, false);


--
-- Name: user_config_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.user_config_id_seq', 36, true);


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
-- Name: tool tool_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tool
    ADD CONSTRAINT tool_pkey PRIMARY KEY (id);


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

CREATE DATABASE timeseries;
-- 可选：授权给 postgres 用户
GRANT ALL PRIVILEGES ON DATABASE timeseries TO postgres;