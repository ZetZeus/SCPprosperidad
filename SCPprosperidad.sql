PGDMP         ;                {            SCPProsperidad    15.0    15.0 `    �           0    0    ENCODING    ENCODING        SET client_encoding = 'UTF8';
                      false            �           0    0 
   STDSTRINGS 
   STDSTRINGS     (   SET standard_conforming_strings = 'on';
                      false            �           0    0 
   SEARCHPATH 
   SEARCHPATH     8   SELECT pg_catalog.set_config('search_path', '', false);
                      false            �           1262    24576    SCPProsperidad    DATABASE     �   CREATE DATABASE "SCPProsperidad" WITH TEMPLATE = template0 ENCODING = 'UTF8' LOCALE_PROVIDER = libc LOCALE = 'Spanish_Chile.1252';
     DROP DATABASE "SCPProsperidad";
                postgres    false            �            1259    24577    Area    TABLE     �   CREATE TABLE public."Area" (
    id_area integer NOT NULL,
    codigo_area character varying(255),
    nombre_area character varying(255)
);
    DROP TABLE public."Area";
       public         heap    postgres    false            �            1259    24584    CentroTrabajo    TABLE     �   CREATE TABLE public."CentroTrabajo" (
    "id_centroTrabajo" integer NOT NULL,
    id_area integer,
    "codigo_centroTrabajo" character varying(255),
    "nombre_centroTrabajo" character varying(255)
);
 #   DROP TABLE public."CentroTrabajo";
       public         heap    postgres    false            �            1259    24598    Maderas    TABLE     H  CREATE TABLE public."Maderas" (
    id_madera integer NOT NULL,
    "id_centroTrabajo" integer,
    codigo_madera character varying(255),
    espesor double precision,
    ancho double precision,
    largo double precision,
    diametro double precision,
    "volumenxPieza" double precision,
    "cantidadxPaquete" double precision,
    factor double precision,
    piezas double precision,
    "volumenTotal" double precision,
    paquetes double precision,
    "nombre_centroTrabajo" character varying(255),
    reproceso double precision,
    volumenreproceso double precision
);
    DROP TABLE public."Maderas";
       public         heap    postgres    false            �            1259    24591    Maquina    TABLE     �   CREATE TABLE public."Maquina" (
    id_maquina integer NOT NULL,
    "id_centroTrabajo" integer,
    "nombreMaquina" character varying(255),
    "centroTrabajoMaquina" character varying(255)
);
    DROP TABLE public."Maquina";
       public         heap    postgres    false            �            1259    24603    Proceso    TABLE     �  CREATE TABLE public."Proceso" (
    id_proceso integer NOT NULL,
    id_madera integer,
    id_area integer,
    "id_centroTrabajo" integer,
    id_maquina integer,
    codigo_madera character varying(255),
    fecha date,
    "nombre_centroTrabajo" character varying(255),
    nombre_maquina character varying(255),
    "piezasEntrada" integer,
    "piezasSalida" integer,
    "volumenEntrada" double precision,
    "volumenSalida" double precision,
    "piezasRechazoHum" integer,
    "piezasRechazoDef" integer,
    "piezasRechazoProc" integer,
    "volumenRechazoHum" double precision,
    "volumenRechazoDef" double precision,
    "volumenRechazoProc" double precision,
    "piezasReproceso" integer,
    "volumenReproceso" double precision,
    "volumenCalidad" double precision,
    "volumenTotal" double precision,
    "piezasCalidad" integer,
    codigo_madera_ant character varying(255)
);
    DROP TABLE public."Proceso";
       public         heap    postgres    false            �            1259    24781 
   auth_group    TABLE     f   CREATE TABLE public.auth_group (
    id integer NOT NULL,
    name character varying(150) NOT NULL
);
    DROP TABLE public.auth_group;
       public         heap    MPerez    false            �            1259    24780    auth_group_id_seq    SEQUENCE     �   ALTER TABLE public.auth_group ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.auth_group_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);
            public          MPerez    false    226            �            1259    24789    auth_group_permissions    TABLE     �   CREATE TABLE public.auth_group_permissions (
    id bigint NOT NULL,
    group_id integer NOT NULL,
    permission_id integer NOT NULL
);
 *   DROP TABLE public.auth_group_permissions;
       public         heap    MPerez    false            �            1259    24788    auth_group_permissions_id_seq    SEQUENCE     �   ALTER TABLE public.auth_group_permissions ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.auth_group_permissions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);
            public          MPerez    false    228            �            1259    24775    auth_permission    TABLE     �   CREATE TABLE public.auth_permission (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    content_type_id integer NOT NULL,
    codename character varying(100) NOT NULL
);
 #   DROP TABLE public.auth_permission;
       public         heap    MPerez    false            �            1259    24774    auth_permission_id_seq    SEQUENCE     �   ALTER TABLE public.auth_permission ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.auth_permission_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);
            public          MPerez    false    224            �            1259    24795 	   auth_user    TABLE     �  CREATE TABLE public.auth_user (
    id integer NOT NULL,
    password character varying(128) NOT NULL,
    last_login timestamp with time zone,
    is_superuser boolean NOT NULL,
    username character varying(150) NOT NULL,
    first_name character varying(150) NOT NULL,
    last_name character varying(150) NOT NULL,
    email character varying(254) NOT NULL,
    is_staff boolean NOT NULL,
    is_active boolean NOT NULL,
    date_joined timestamp with time zone NOT NULL
);
    DROP TABLE public.auth_user;
       public         heap    MPerez    false            �            1259    24803    auth_user_groups    TABLE     ~   CREATE TABLE public.auth_user_groups (
    id bigint NOT NULL,
    user_id integer NOT NULL,
    group_id integer NOT NULL
);
 $   DROP TABLE public.auth_user_groups;
       public         heap    MPerez    false            �            1259    24802    auth_user_groups_id_seq    SEQUENCE     �   ALTER TABLE public.auth_user_groups ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.auth_user_groups_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);
            public          MPerez    false    232            �            1259    24794    auth_user_id_seq    SEQUENCE     �   ALTER TABLE public.auth_user ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.auth_user_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);
            public          MPerez    false    230            �            1259    24809    auth_user_user_permissions    TABLE     �   CREATE TABLE public.auth_user_user_permissions (
    id bigint NOT NULL,
    user_id integer NOT NULL,
    permission_id integer NOT NULL
);
 .   DROP TABLE public.auth_user_user_permissions;
       public         heap    MPerez    false            �            1259    24808 !   auth_user_user_permissions_id_seq    SEQUENCE     �   ALTER TABLE public.auth_user_user_permissions ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.auth_user_user_permissions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);
            public          MPerez    false    234            �            1259    24867    django_admin_log    TABLE     �  CREATE TABLE public.django_admin_log (
    id integer NOT NULL,
    action_time timestamp with time zone NOT NULL,
    object_id text,
    object_repr character varying(200) NOT NULL,
    action_flag smallint NOT NULL,
    change_message text NOT NULL,
    content_type_id integer,
    user_id integer NOT NULL,
    CONSTRAINT django_admin_log_action_flag_check CHECK ((action_flag >= 0))
);
 $   DROP TABLE public.django_admin_log;
       public         heap    MPerez    false            �            1259    24866    django_admin_log_id_seq    SEQUENCE     �   ALTER TABLE public.django_admin_log ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.django_admin_log_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);
            public          MPerez    false    236            �            1259    24767    django_content_type    TABLE     �   CREATE TABLE public.django_content_type (
    id integer NOT NULL,
    app_label character varying(100) NOT NULL,
    model character varying(100) NOT NULL
);
 '   DROP TABLE public.django_content_type;
       public         heap    MPerez    false            �            1259    24766    django_content_type_id_seq    SEQUENCE     �   ALTER TABLE public.django_content_type ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.django_content_type_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);
            public          MPerez    false    222            �            1259    24759    django_migrations    TABLE     �   CREATE TABLE public.django_migrations (
    id bigint NOT NULL,
    app character varying(255) NOT NULL,
    name character varying(255) NOT NULL,
    applied timestamp with time zone NOT NULL
);
 %   DROP TABLE public.django_migrations;
       public         heap    MPerez    false            �            1259    24758    django_migrations_id_seq    SEQUENCE     �   ALTER TABLE public.django_migrations ALTER COLUMN id ADD GENERATED BY DEFAULT AS IDENTITY (
    SEQUENCE NAME public.django_migrations_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);
            public          MPerez    false    220            �            1259    24895    django_session    TABLE     �   CREATE TABLE public.django_session (
    session_key character varying(40) NOT NULL,
    session_data text NOT NULL,
    expire_date timestamp with time zone NOT NULL
);
 "   DROP TABLE public.django_session;
       public         heap    MPerez    false            v          0    24577    Area 
   TABLE DATA           C   COPY public."Area" (id_area, codigo_area, nombre_area) FROM stdin;
    public          postgres    false    214   ݆       w          0    24584    CentroTrabajo 
   TABLE DATA           v   COPY public."CentroTrabajo" ("id_centroTrabajo", id_area, "codigo_centroTrabajo", "nombre_centroTrabajo") FROM stdin;
    public          postgres    false    215   �       y          0    24598    Maderas 
   TABLE DATA           �   COPY public."Maderas" (id_madera, "id_centroTrabajo", codigo_madera, espesor, ancho, largo, diametro, "volumenxPieza", "cantidadxPaquete", factor, piezas, "volumenTotal", paquetes, "nombre_centroTrabajo", reproceso, volumenreproceso) FROM stdin;
    public          postgres    false    217   ��       x          0    24591    Maquina 
   TABLE DATA           l   COPY public."Maquina" (id_maquina, "id_centroTrabajo", "nombreMaquina", "centroTrabajoMaquina") FROM stdin;
    public          postgres    false    216   l�       z          0    24603    Proceso 
   TABLE DATA           �  COPY public."Proceso" (id_proceso, id_madera, id_area, "id_centroTrabajo", id_maquina, codigo_madera, fecha, "nombre_centroTrabajo", nombre_maquina, "piezasEntrada", "piezasSalida", "volumenEntrada", "volumenSalida", "piezasRechazoHum", "piezasRechazoDef", "piezasRechazoProc", "volumenRechazoHum", "volumenRechazoDef", "volumenRechazoProc", "piezasReproceso", "volumenReproceso", "volumenCalidad", "volumenTotal", "piezasCalidad", codigo_madera_ant) FROM stdin;
    public          postgres    false    218   �       �          0    24781 
   auth_group 
   TABLE DATA           .   COPY public.auth_group (id, name) FROM stdin;
    public          MPerez    false    226   �       �          0    24789    auth_group_permissions 
   TABLE DATA           M   COPY public.auth_group_permissions (id, group_id, permission_id) FROM stdin;
    public          MPerez    false    228   0�       �          0    24775    auth_permission 
   TABLE DATA           N   COPY public.auth_permission (id, name, content_type_id, codename) FROM stdin;
    public          MPerez    false    224   M�       �          0    24795 	   auth_user 
   TABLE DATA           �   COPY public.auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) FROM stdin;
    public          MPerez    false    230   j�       �          0    24803    auth_user_groups 
   TABLE DATA           A   COPY public.auth_user_groups (id, user_id, group_id) FROM stdin;
    public          MPerez    false    232   #�       �          0    24809    auth_user_user_permissions 
   TABLE DATA           P   COPY public.auth_user_user_permissions (id, user_id, permission_id) FROM stdin;
    public          MPerez    false    234   @�       �          0    24867    django_admin_log 
   TABLE DATA           �   COPY public.django_admin_log (id, action_time, object_id, object_repr, action_flag, change_message, content_type_id, user_id) FROM stdin;
    public          MPerez    false    236   ]�       ~          0    24767    django_content_type 
   TABLE DATA           C   COPY public.django_content_type (id, app_label, model) FROM stdin;
    public          MPerez    false    222   ʔ       |          0    24759    django_migrations 
   TABLE DATA           C   COPY public.django_migrations (id, app, name, applied) FROM stdin;
    public          MPerez    false    220   G�       �          0    24895    django_session 
   TABLE DATA           P   COPY public.django_session (session_key, session_data, expire_date) FROM stdin;
    public          MPerez    false    237   �       �           0    0    auth_group_id_seq    SEQUENCE SET     @   SELECT pg_catalog.setval('public.auth_group_id_seq', 1, false);
          public          MPerez    false    225            �           0    0    auth_group_permissions_id_seq    SEQUENCE SET     L   SELECT pg_catalog.setval('public.auth_group_permissions_id_seq', 1, false);
          public          MPerez    false    227            �           0    0    auth_permission_id_seq    SEQUENCE SET     E   SELECT pg_catalog.setval('public.auth_permission_id_seq', 24, true);
          public          MPerez    false    223            �           0    0    auth_user_groups_id_seq    SEQUENCE SET     F   SELECT pg_catalog.setval('public.auth_user_groups_id_seq', 1, false);
          public          MPerez    false    231            �           0    0    auth_user_id_seq    SEQUENCE SET     >   SELECT pg_catalog.setval('public.auth_user_id_seq', 1, true);
          public          MPerez    false    229            �           0    0 !   auth_user_user_permissions_id_seq    SEQUENCE SET     P   SELECT pg_catalog.setval('public.auth_user_user_permissions_id_seq', 1, false);
          public          MPerez    false    233            �           0    0    django_admin_log_id_seq    SEQUENCE SET     E   SELECT pg_catalog.setval('public.django_admin_log_id_seq', 1, true);
          public          MPerez    false    235            �           0    0    django_content_type_id_seq    SEQUENCE SET     H   SELECT pg_catalog.setval('public.django_content_type_id_seq', 7, true);
          public          MPerez    false    221            �           0    0    django_migrations_id_seq    SEQUENCE SET     G   SELECT pg_catalog.setval('public.django_migrations_id_seq', 18, true);
          public          MPerez    false    219            �           2606    24583    Area Area_pkey 
   CONSTRAINT     U   ALTER TABLE ONLY public."Area"
    ADD CONSTRAINT "Area_pkey" PRIMARY KEY (id_area);
 <   ALTER TABLE ONLY public."Area" DROP CONSTRAINT "Area_pkey";
       public            postgres    false    214            �           2606    24590     CentroTrabajo CentroTrabajo_pkey 
   CONSTRAINT     r   ALTER TABLE ONLY public."CentroTrabajo"
    ADD CONSTRAINT "CentroTrabajo_pkey" PRIMARY KEY ("id_centroTrabajo");
 N   ALTER TABLE ONLY public."CentroTrabajo" DROP CONSTRAINT "CentroTrabajo_pkey";
       public            postgres    false    215            �           2606    24602    Maderas Maderas_pkey 
   CONSTRAINT     ]   ALTER TABLE ONLY public."Maderas"
    ADD CONSTRAINT "Maderas_pkey" PRIMARY KEY (id_madera);
 B   ALTER TABLE ONLY public."Maderas" DROP CONSTRAINT "Maderas_pkey";
       public            postgres    false    217            �           2606    24597    Maquina Maquina_pkey 
   CONSTRAINT     ^   ALTER TABLE ONLY public."Maquina"
    ADD CONSTRAINT "Maquina_pkey" PRIMARY KEY (id_maquina);
 B   ALTER TABLE ONLY public."Maquina" DROP CONSTRAINT "Maquina_pkey";
       public            postgres    false    216            �           2606    24609    Proceso Proceso_pkey 
   CONSTRAINT     ^   ALTER TABLE ONLY public."Proceso"
    ADD CONSTRAINT "Proceso_pkey" PRIMARY KEY (id_proceso);
 B   ALTER TABLE ONLY public."Proceso" DROP CONSTRAINT "Proceso_pkey";
       public            postgres    false    218            �           2606    24893    auth_group auth_group_name_key 
   CONSTRAINT     Y   ALTER TABLE ONLY public.auth_group
    ADD CONSTRAINT auth_group_name_key UNIQUE (name);
 H   ALTER TABLE ONLY public.auth_group DROP CONSTRAINT auth_group_name_key;
       public            MPerez    false    226            �           2606    24824 R   auth_group_permissions auth_group_permissions_group_id_permission_id_0cd325b0_uniq 
   CONSTRAINT     �   ALTER TABLE ONLY public.auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_group_id_permission_id_0cd325b0_uniq UNIQUE (group_id, permission_id);
 |   ALTER TABLE ONLY public.auth_group_permissions DROP CONSTRAINT auth_group_permissions_group_id_permission_id_0cd325b0_uniq;
       public            MPerez    false    228    228            �           2606    24793 2   auth_group_permissions auth_group_permissions_pkey 
   CONSTRAINT     p   ALTER TABLE ONLY public.auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_pkey PRIMARY KEY (id);
 \   ALTER TABLE ONLY public.auth_group_permissions DROP CONSTRAINT auth_group_permissions_pkey;
       public            MPerez    false    228            �           2606    24785    auth_group auth_group_pkey 
   CONSTRAINT     X   ALTER TABLE ONLY public.auth_group
    ADD CONSTRAINT auth_group_pkey PRIMARY KEY (id);
 D   ALTER TABLE ONLY public.auth_group DROP CONSTRAINT auth_group_pkey;
       public            MPerez    false    226            �           2606    24815 F   auth_permission auth_permission_content_type_id_codename_01ab375a_uniq 
   CONSTRAINT     �   ALTER TABLE ONLY public.auth_permission
    ADD CONSTRAINT auth_permission_content_type_id_codename_01ab375a_uniq UNIQUE (content_type_id, codename);
 p   ALTER TABLE ONLY public.auth_permission DROP CONSTRAINT auth_permission_content_type_id_codename_01ab375a_uniq;
       public            MPerez    false    224    224            �           2606    24779 $   auth_permission auth_permission_pkey 
   CONSTRAINT     b   ALTER TABLE ONLY public.auth_permission
    ADD CONSTRAINT auth_permission_pkey PRIMARY KEY (id);
 N   ALTER TABLE ONLY public.auth_permission DROP CONSTRAINT auth_permission_pkey;
       public            MPerez    false    224            �           2606    24807 &   auth_user_groups auth_user_groups_pkey 
   CONSTRAINT     d   ALTER TABLE ONLY public.auth_user_groups
    ADD CONSTRAINT auth_user_groups_pkey PRIMARY KEY (id);
 P   ALTER TABLE ONLY public.auth_user_groups DROP CONSTRAINT auth_user_groups_pkey;
       public            MPerez    false    232            �           2606    24839 @   auth_user_groups auth_user_groups_user_id_group_id_94350c0c_uniq 
   CONSTRAINT     �   ALTER TABLE ONLY public.auth_user_groups
    ADD CONSTRAINT auth_user_groups_user_id_group_id_94350c0c_uniq UNIQUE (user_id, group_id);
 j   ALTER TABLE ONLY public.auth_user_groups DROP CONSTRAINT auth_user_groups_user_id_group_id_94350c0c_uniq;
       public            MPerez    false    232    232            �           2606    24799    auth_user auth_user_pkey 
   CONSTRAINT     V   ALTER TABLE ONLY public.auth_user
    ADD CONSTRAINT auth_user_pkey PRIMARY KEY (id);
 B   ALTER TABLE ONLY public.auth_user DROP CONSTRAINT auth_user_pkey;
       public            MPerez    false    230            �           2606    24813 :   auth_user_user_permissions auth_user_user_permissions_pkey 
   CONSTRAINT     x   ALTER TABLE ONLY public.auth_user_user_permissions
    ADD CONSTRAINT auth_user_user_permissions_pkey PRIMARY KEY (id);
 d   ALTER TABLE ONLY public.auth_user_user_permissions DROP CONSTRAINT auth_user_user_permissions_pkey;
       public            MPerez    false    234            �           2606    24853 Y   auth_user_user_permissions auth_user_user_permissions_user_id_permission_id_14a6b632_uniq 
   CONSTRAINT     �   ALTER TABLE ONLY public.auth_user_user_permissions
    ADD CONSTRAINT auth_user_user_permissions_user_id_permission_id_14a6b632_uniq UNIQUE (user_id, permission_id);
 �   ALTER TABLE ONLY public.auth_user_user_permissions DROP CONSTRAINT auth_user_user_permissions_user_id_permission_id_14a6b632_uniq;
       public            MPerez    false    234    234            �           2606    24888     auth_user auth_user_username_key 
   CONSTRAINT     _   ALTER TABLE ONLY public.auth_user
    ADD CONSTRAINT auth_user_username_key UNIQUE (username);
 J   ALTER TABLE ONLY public.auth_user DROP CONSTRAINT auth_user_username_key;
       public            MPerez    false    230            �           2606    24874 &   django_admin_log django_admin_log_pkey 
   CONSTRAINT     d   ALTER TABLE ONLY public.django_admin_log
    ADD CONSTRAINT django_admin_log_pkey PRIMARY KEY (id);
 P   ALTER TABLE ONLY public.django_admin_log DROP CONSTRAINT django_admin_log_pkey;
       public            MPerez    false    236            �           2606    24773 E   django_content_type django_content_type_app_label_model_76bd3d3b_uniq 
   CONSTRAINT     �   ALTER TABLE ONLY public.django_content_type
    ADD CONSTRAINT django_content_type_app_label_model_76bd3d3b_uniq UNIQUE (app_label, model);
 o   ALTER TABLE ONLY public.django_content_type DROP CONSTRAINT django_content_type_app_label_model_76bd3d3b_uniq;
       public            MPerez    false    222    222            �           2606    24771 ,   django_content_type django_content_type_pkey 
   CONSTRAINT     j   ALTER TABLE ONLY public.django_content_type
    ADD CONSTRAINT django_content_type_pkey PRIMARY KEY (id);
 V   ALTER TABLE ONLY public.django_content_type DROP CONSTRAINT django_content_type_pkey;
       public            MPerez    false    222            �           2606    24765 (   django_migrations django_migrations_pkey 
   CONSTRAINT     f   ALTER TABLE ONLY public.django_migrations
    ADD CONSTRAINT django_migrations_pkey PRIMARY KEY (id);
 R   ALTER TABLE ONLY public.django_migrations DROP CONSTRAINT django_migrations_pkey;
       public            MPerez    false    220            �           2606    24901 "   django_session django_session_pkey 
   CONSTRAINT     i   ALTER TABLE ONLY public.django_session
    ADD CONSTRAINT django_session_pkey PRIMARY KEY (session_key);
 L   ALTER TABLE ONLY public.django_session DROP CONSTRAINT django_session_pkey;
       public            MPerez    false    237            �           1259    24894    auth_group_name_a6ea08ec_like    INDEX     h   CREATE INDEX auth_group_name_a6ea08ec_like ON public.auth_group USING btree (name varchar_pattern_ops);
 1   DROP INDEX public.auth_group_name_a6ea08ec_like;
       public            MPerez    false    226            �           1259    24835 (   auth_group_permissions_group_id_b120cbf9    INDEX     o   CREATE INDEX auth_group_permissions_group_id_b120cbf9 ON public.auth_group_permissions USING btree (group_id);
 <   DROP INDEX public.auth_group_permissions_group_id_b120cbf9;
       public            MPerez    false    228            �           1259    24836 -   auth_group_permissions_permission_id_84c5c92e    INDEX     y   CREATE INDEX auth_group_permissions_permission_id_84c5c92e ON public.auth_group_permissions USING btree (permission_id);
 A   DROP INDEX public.auth_group_permissions_permission_id_84c5c92e;
       public            MPerez    false    228            �           1259    24821 (   auth_permission_content_type_id_2f476e4b    INDEX     o   CREATE INDEX auth_permission_content_type_id_2f476e4b ON public.auth_permission USING btree (content_type_id);
 <   DROP INDEX public.auth_permission_content_type_id_2f476e4b;
       public            MPerez    false    224            �           1259    24851 "   auth_user_groups_group_id_97559544    INDEX     c   CREATE INDEX auth_user_groups_group_id_97559544 ON public.auth_user_groups USING btree (group_id);
 6   DROP INDEX public.auth_user_groups_group_id_97559544;
       public            MPerez    false    232            �           1259    24850 !   auth_user_groups_user_id_6a12ed8b    INDEX     a   CREATE INDEX auth_user_groups_user_id_6a12ed8b ON public.auth_user_groups USING btree (user_id);
 5   DROP INDEX public.auth_user_groups_user_id_6a12ed8b;
       public            MPerez    false    232            �           1259    24865 1   auth_user_user_permissions_permission_id_1fbb5f2c    INDEX     �   CREATE INDEX auth_user_user_permissions_permission_id_1fbb5f2c ON public.auth_user_user_permissions USING btree (permission_id);
 E   DROP INDEX public.auth_user_user_permissions_permission_id_1fbb5f2c;
       public            MPerez    false    234            �           1259    24864 +   auth_user_user_permissions_user_id_a95ead1b    INDEX     u   CREATE INDEX auth_user_user_permissions_user_id_a95ead1b ON public.auth_user_user_permissions USING btree (user_id);
 ?   DROP INDEX public.auth_user_user_permissions_user_id_a95ead1b;
       public            MPerez    false    234            �           1259    24889     auth_user_username_6821ab7c_like    INDEX     n   CREATE INDEX auth_user_username_6821ab7c_like ON public.auth_user USING btree (username varchar_pattern_ops);
 4   DROP INDEX public.auth_user_username_6821ab7c_like;
       public            MPerez    false    230            �           1259    24885 )   django_admin_log_content_type_id_c4bce8eb    INDEX     q   CREATE INDEX django_admin_log_content_type_id_c4bce8eb ON public.django_admin_log USING btree (content_type_id);
 =   DROP INDEX public.django_admin_log_content_type_id_c4bce8eb;
       public            MPerez    false    236            �           1259    24886 !   django_admin_log_user_id_c564eba6    INDEX     a   CREATE INDEX django_admin_log_user_id_c564eba6 ON public.django_admin_log USING btree (user_id);
 5   DROP INDEX public.django_admin_log_user_id_c564eba6;
       public            MPerez    false    236            �           1259    24903 #   django_session_expire_date_a5c62663    INDEX     e   CREATE INDEX django_session_expire_date_a5c62663 ON public.django_session USING btree (expire_date);
 7   DROP INDEX public.django_session_expire_date_a5c62663;
       public            MPerez    false    237            �           1259    24902 (   django_session_session_key_c0390e0f_like    INDEX     ~   CREATE INDEX django_session_session_key_c0390e0f_like ON public.django_session USING btree (session_key varchar_pattern_ops);
 <   DROP INDEX public.django_session_session_key_c0390e0f_like;
       public            MPerez    false    237            �           2606    24830 O   auth_group_permissions auth_group_permissio_permission_id_84c5c92e_fk_auth_perm    FK CONSTRAINT     �   ALTER TABLE ONLY public.auth_group_permissions
    ADD CONSTRAINT auth_group_permissio_permission_id_84c5c92e_fk_auth_perm FOREIGN KEY (permission_id) REFERENCES public.auth_permission(id) DEFERRABLE INITIALLY DEFERRED;
 y   ALTER TABLE ONLY public.auth_group_permissions DROP CONSTRAINT auth_group_permissio_permission_id_84c5c92e_fk_auth_perm;
       public          MPerez    false    228    3258    224            �           2606    24825 P   auth_group_permissions auth_group_permissions_group_id_b120cbf9_fk_auth_group_id    FK CONSTRAINT     �   ALTER TABLE ONLY public.auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_group_id_b120cbf9_fk_auth_group_id FOREIGN KEY (group_id) REFERENCES public.auth_group(id) DEFERRABLE INITIALLY DEFERRED;
 z   ALTER TABLE ONLY public.auth_group_permissions DROP CONSTRAINT auth_group_permissions_group_id_b120cbf9_fk_auth_group_id;
       public          MPerez    false    3263    228    226            �           2606    24816 E   auth_permission auth_permission_content_type_id_2f476e4b_fk_django_co    FK CONSTRAINT     �   ALTER TABLE ONLY public.auth_permission
    ADD CONSTRAINT auth_permission_content_type_id_2f476e4b_fk_django_co FOREIGN KEY (content_type_id) REFERENCES public.django_content_type(id) DEFERRABLE INITIALLY DEFERRED;
 o   ALTER TABLE ONLY public.auth_permission DROP CONSTRAINT auth_permission_content_type_id_2f476e4b_fk_django_co;
       public          MPerez    false    222    3253    224            �           2606    24845 D   auth_user_groups auth_user_groups_group_id_97559544_fk_auth_group_id    FK CONSTRAINT     �   ALTER TABLE ONLY public.auth_user_groups
    ADD CONSTRAINT auth_user_groups_group_id_97559544_fk_auth_group_id FOREIGN KEY (group_id) REFERENCES public.auth_group(id) DEFERRABLE INITIALLY DEFERRED;
 n   ALTER TABLE ONLY public.auth_user_groups DROP CONSTRAINT auth_user_groups_group_id_97559544_fk_auth_group_id;
       public          MPerez    false    3263    232    226            �           2606    24840 B   auth_user_groups auth_user_groups_user_id_6a12ed8b_fk_auth_user_id    FK CONSTRAINT     �   ALTER TABLE ONLY public.auth_user_groups
    ADD CONSTRAINT auth_user_groups_user_id_6a12ed8b_fk_auth_user_id FOREIGN KEY (user_id) REFERENCES public.auth_user(id) DEFERRABLE INITIALLY DEFERRED;
 l   ALTER TABLE ONLY public.auth_user_groups DROP CONSTRAINT auth_user_groups_user_id_6a12ed8b_fk_auth_user_id;
       public          MPerez    false    232    3271    230            �           2606    24859 S   auth_user_user_permissions auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm    FK CONSTRAINT     �   ALTER TABLE ONLY public.auth_user_user_permissions
    ADD CONSTRAINT auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm FOREIGN KEY (permission_id) REFERENCES public.auth_permission(id) DEFERRABLE INITIALLY DEFERRED;
 }   ALTER TABLE ONLY public.auth_user_user_permissions DROP CONSTRAINT auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm;
       public          MPerez    false    234    224    3258            �           2606    24854 V   auth_user_user_permissions auth_user_user_permissions_user_id_a95ead1b_fk_auth_user_id    FK CONSTRAINT     �   ALTER TABLE ONLY public.auth_user_user_permissions
    ADD CONSTRAINT auth_user_user_permissions_user_id_a95ead1b_fk_auth_user_id FOREIGN KEY (user_id) REFERENCES public.auth_user(id) DEFERRABLE INITIALLY DEFERRED;
 �   ALTER TABLE ONLY public.auth_user_user_permissions DROP CONSTRAINT auth_user_user_permissions_user_id_a95ead1b_fk_auth_user_id;
       public          MPerez    false    230    234    3271            �           2606    24875 G   django_admin_log django_admin_log_content_type_id_c4bce8eb_fk_django_co    FK CONSTRAINT     �   ALTER TABLE ONLY public.django_admin_log
    ADD CONSTRAINT django_admin_log_content_type_id_c4bce8eb_fk_django_co FOREIGN KEY (content_type_id) REFERENCES public.django_content_type(id) DEFERRABLE INITIALLY DEFERRED;
 q   ALTER TABLE ONLY public.django_admin_log DROP CONSTRAINT django_admin_log_content_type_id_c4bce8eb_fk_django_co;
       public          MPerez    false    222    236    3253            �           2606    24880 B   django_admin_log django_admin_log_user_id_c564eba6_fk_auth_user_id    FK CONSTRAINT     �   ALTER TABLE ONLY public.django_admin_log
    ADD CONSTRAINT django_admin_log_user_id_c564eba6_fk_auth_user_id FOREIGN KEY (user_id) REFERENCES public.auth_user(id) DEFERRABLE INITIALLY DEFERRED;
 l   ALTER TABLE ONLY public.django_admin_log DROP CONSTRAINT django_admin_log_user_id_c564eba6_fk_auth_user_id;
       public          MPerez    false    230    236    3271            v   $   x�3�440�J�M�2�42C�rR��b���� fD�      w   y   x�U���@��� _�-B�� %����I�8r���K����&$pb���K�㦾��QM˸�,٨�']K�a�0�>�Z��}=�����<0.ey��81�V��Յ�0#㦫۬���@D?�P)5      y   �  x����N�@��λd4�x���$��V-+�ME�@B�_�Ʉ6�"�J�T����{H����5:��,8�`��6����n0h|����4��Z�bp���W���q$"��"*�s$b+�2�y`9��}Zf&B��m�P8�8KɒʒBv�;�;�9�0B��f[�Q������Iz3�ö}?��ۏS_8��Œ-�	D����t&�,�;���2ƭ3���ñ`r���1�F��g�SFՆ&f��Inv�/�܋�DwE>�����p�ўχc{>�3��r�=;,Le��;�S����%P�dǏx���ɺ�S��W�6������O�u]S�z=+R=j�^����򌋉����o���-�K�f#�"�향�� q�R�lA�3H�E)�II+!N\��g7���h��
��*r�M��d�Ireػ�����7�      x   �   x�M���0E���(cU�	�ԅ�J�*R���.|=�Đ��9���f��ΓnL�&�,A�rX�IH���aKCP
�dZ~�i�Q�
W�G���ƒ�,xJ��kz�4/1��#Ę$�ѳ�n�=L�*,���x/3�Չ(S�%�����pL�먔�XOGg      z   �  x��[�n�6}��?�9�?�S����P����Y�u�N^��^$QE�Խ8���҈�p83�!��b�#�����;`@T@�o��P�nv?����R=���x}������ZqJQ�V�GR����?�?��@����t7b��8��xx�f��6�~ʟۧ��z�m�Zw�9[�8 r< �� �"�ezZ�E ����%*Zk�ZuP�f���?�F��4L��N��RO��B2	--�U+��d�����:jiG�+0?�RNQc�1�-�܋����t�����������q^7��Eӑh��4�N=	/�Xő��t���/daE_�/�z=<m����S�&!4�2Q����$�)��5)N��Q����ms�������R{�������6�ϳZ1�&��"%7R9�ҚA� m�At7�x傂F��q���}�W�/߾�<���������7ݠbH�uV BT���˦Vk����h�z�J�,�����z�`d�`�uF5�
���Rcu���[���٪-~<�y$��%R��%RVfI�Z�-�X>cP��H��=�J�!Y��q�o�+g�����Nl()+ٛ�Rt0��7��Z����Z��#)�0xy&ҳ�N�K3ڇ/Ʈ�4A�7G��͈�FJ�:.g���A�!�
�DwQ�(MIP)IG	�ԃ)���"��jqҙ�&P��~^7E=���l�fg�-�:�V4��8�"a8/%WI�5J�<�*���QZ��N�s}Fr�}�բ�[�eIg"yV<�4k�1[�r*Sΐ�ʧ���{)��'[LE����<���d6Z�ZeZ�ƨ]�ﲣ����(�R�4�VO���Ö�mo�!�˙��ZQ�Y�w��w�@�y���n2V�9C<E��2s,*�'�=f
oe���D�K��p[Z�
����s��CcSzQ���伶�Q��f'/e�R@�R@�2@-�}�n���1�"T兂U��p�~�+`��]P2"�Q��j�Օ_쳹աU��,ou��\��~��k
��$�\s_���Gl����k�V��M;,0�F?-�C�Ů�}̶ֹ��V�@��,�le���_v���'蠩I�������K\kq(����N8|�5A��X���:�d�!ʬ3��f�8��(&5Rj�6~��({.�_������ze,:v��f�c�������2�gF�$"xv�ێw��f
��l�as��\�grm8TR�ݻ�S�/-	y�<�1��)���f�lF��ә4��b��S�6F� O�[�X�r�v-���c�p�Cժ���D�c�f�$R+6�m�h6����.��
C�;��;b�I,x�o�ף�Nw�$��ݱ�;犮ֳi)�B�{�.��T߷��Dx���>M�
�FO��z4�}\tpM%t$['f�x�`�23��H<����r�d����sE,W�ff=)�ڜ:��o�N�؊N��P'�\L9Yۚ�c�
��i������'�ATu���6�Ml%��TP�u���������1�TeQ��D��t�{W�-�C+@�L9O��z�.}�3�6Q�CWA�k��nyQ��.�s�Ce�9f:�j�QN�;��Ə(��نI�Ga:��i���r9��JA}F���bu�)���3�$z�vM�y�e��Z��G7T˻�c>I��f�3��t�6؆	�j��QX�?ד��C��'a��	�|�ޞ�KswF����3�j�l��.xP%9���:=�`���"�N��)�%x�ey��h��kIk&��Ȥ<C-ɨ�/���r۫��/?�lFMa�aG��GU�ḁ;����aS�z�]p���!�7A@6�H��)�(��d����7��4ԍ9d�D�_������������6��r��f08f�lNQ-�9������Ѣ����dZ���}U�&�dƹ:z�����|b+شS��3�Q�k���pXvXX	�Z�5�|%�ja�-�z��a�<��Z�U�90��q�-��5!�?4C#u      �      x������ � �      �      x������ � �      �     x�]�K��0��ur
N0j£�z�Q�B�b�:�h�����I�%��o��i�g�f��c�Y����G�<��ЂRq�0G��f�a����[�m��Le���4u}0�x`+� �	{�}�R��NT����v�����֝d�~O]D�l�	�����<,�����ӺB�[ZA)���T���qu�<�͏>��_��� ��m�.2�)H���:x�ޟ8�1WY��'���`:Y��;�LL�vf���x댰j'�k�2�      �   �   x�3�,H�NI3�/�H425S13 W_�`���ࢢ�� �̲���2��(W���@w���47Ӡ����@Ϭ���À����p󪲌l[N##c]3]CK+S+#=CKSK��	g	gbJnf''�vH�H�-�I�K��ʕ`�64�3476�4������ �%3�      �      x������ � �      �      x������ � �      �   ]   x��9�  �zy����"G�3���BBG��3�"q�H}0.�V�ovqW0����j��[x���4>��.bJ9���X v*����q      ~   m   x�M�;�@Dk�a��'�܃�kYD��-r{ݼ�<�@<�U�eE4}���烚�\#�)[S�z�q��8��4W-�&�)�k�/�L�KU���:��Y:��i�� ��/�      |   �  x���Mn� F��)z�T��g��PB]$l\�Us�vI�:J6l���y���d��.��B��l��uarD����7��0e���p����8�1"����y��J���V���pQ���ۨ|�W�|�g0���2ȕ�sJ�����pzP�OoO��>�Ǣ������l��I�f%&%�?��K&�ل��XJ*y5���4�vQ=`�7�PK̋�u�)$-�(��R�Z���=�êPc�[��1�6w���K��� 4
�v����]iw h6�Χ�J��Ξu�!��7!��F��\��<Ekg���];4�kG��H��PI\Q�hC�/�sZ�WoP˜5�s���;~G�Bg��]}��l[�!���.��ԇ�
�cI�;=�#�Y�      �   	  x��ݲB@  ��<�y�ZK��
�Y�TRsf����Fv�����A��L���j}�
\�s6����ۣ�M�q�8�u���0'w��Ylz̭�9Tmu P�y�i���pE�o���[8�򀶚� ��-��&��n"�i�`T��vLGxc�)Fy�n#8��`��֛�qZ2�0���]��vtt_���6�G�Z -�ҡGIMw��p�_�Z�t�\_��Nvޜ!ROn]g��F���@��`SC&�S�X�2@��T��,e\      