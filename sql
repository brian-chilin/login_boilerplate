-- Dumped from database version 16.10 (Debian 16.10-1.pgdg13+1)
-- Dumped by pg_dump version 16.10

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

--
-- TOC entry 216 (class 1259 OID 16390)
-- Name: users; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.users (
    id integer NOT NULL,
    username character varying(255) NOT NULL,
    password character varying(255) NOT NULL,
    raw_password character varying(255)
);


--
-- TOC entry 215 (class 1259 OID 16389)
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 3419 (class 0 OID 0)
-- Dependencies: 215
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- TOC entry 3266 (class 2604 OID 16393)
-- Name: users id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- TOC entry 3413 (class 0 OID 16390)
-- Dependencies: 216
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.users (id, username, password, raw_password) FROM stdin;
6	matthew	$argon2id$v=19$m=65536,t=3,p=4$NJBlmaX3DRnojdR+kaRkZg$0LlzOUpeShZtM77HYbErMQV/oXSNXAAQVXSwE3Zk7gw	hidden4
5	luke	$argon2id$v=19$m=65536,t=3,p=4$ODQym2UdCPimaOJqgjE9Qg$AJj4t54u/bBPTCgkEWUUbt73rNM51AN9KGQ/RyCHcmk	johncenaBIGGESTfan
4	john	$argon2id$v=19$m=65536,t=3,p=4$USK6Zo++BE8QwQZ8+FK85A$Xqf+7pkXWSfqBPgK0d7Bg/ONt6jRmFz0bYfPV7lT4bY	\N
3	charlie	$argon2id$v=19$m=65536,t=3,p=4$TceWl1Tsboi+C9GvpzJ76w$zzgpDKCjQxO4LmpteXVUg8dnVlnkDwdg+5qyFFRmQ5E	\N
2	blake	$argon2id$v=19$m=65536,t=3,p=4$g86xuDIfUMOABiVLwSbCBA$oD7odDDm3GKdwyNLjRq2stfJ2p4HQoLlbBPGNjEvzP0	poniesRcool1
1	abraham	$argon2id$v=19$m=65536,t=3,p=4$vXBgp1vgacURkOYuZXAA1Q$R5wplzqQYPd/fEPlEaXIYh+E4DOVz9Zd9Kix4+tODVk	verysecret7
\.


--
-- TOC entry 3420 (class 0 OID 0)
-- Dependencies: 215
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.users_id_seq', 6, true);


--
-- TOC entry 3268 (class 2606 OID 16397)
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);

--
-- PostgreSQL database dump complete
--
