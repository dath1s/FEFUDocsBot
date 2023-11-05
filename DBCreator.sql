CREATE TABLE public."Users" (
	id serial4 NOT NULL,
	user_telegram_id int8 NOT NULL,
	fullname varchar(100) NOT NULL,
	folder_name text NOT NULL DEFAULT '-'::text
);

CREATE TABLE public."Documents" (
	user_id int8 NOT NULL,
	passport text NOT NULL DEFAULT '-'::text,
	inn text NOT NULL DEFAULT '-'::text,
	snils text NOT NULL DEFAULT '-'::text,
	bank_statement text NOT NULL DEFAULT '-'::text,
	pd text NOT NULL DEFAULT '-'::text,
	military_ticket text NOT NULL DEFAULT '-'::text,
	education_document text NOT NULL DEFAULT '-'::text,
	study_certificate text NOT NULL DEFAULT '-'::text,
	stdr_form text NOT NULL DEFAULT '-'::text,
	marriage_certificate text NOT NULL DEFAULT '-'::text,
	change_name_certificate text NOT NULL DEFAULT '-'::text,
	kids_born_certificate text NOT NULL DEFAULT '-'::text,
	no_criminal_certificate text NOT NULL DEFAULT '-'::text,
	passport2 text NOT NULL DEFAULT '-'::text
);

CREATE TABLE public."Applications" (
	user_id int8 NOT NULL,
	application_type text NOT NULL DEFAULT 'Нет действительной заявки'::text,
	status text NOT NULL DEFAULT 'Нет действительной заявки'::text,
	"date" text NOT NULL DEFAULT '-'::text,
	"comment" text NULL
);
