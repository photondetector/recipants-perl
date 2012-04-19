-- File:		tables_postgres.sql
-- Description:	DDL for ReciPants schema, Postgres version
-- Author:		Nick Grossman <nick@photondetector.com>
-- Tab stops:	4
-- Version:		1.1.1


------------
-- TABLES --
------------


CREATE TABLE categories (
	category_id 		SERIAL			NOT NULL,
	parent 				INT4 			NOT NULL,
	name 				VARCHAR(256)	NOT NULL,
	CONSTRAINT 			pk_categories PRIMARY KEY (category_id)
);


CREATE TABLE category_entries (
	recipe_id 			INT4 			NOT NULL,
	category_id			INT4 			NOT NULL,
	CONSTRAINT			pk_category_entries PRIMARY KEY (recipe_id, category_id)
);


CREATE TABLE ingredient_types (
	ingredient_type		SERIAL			NOT NULL,
	name 				VARCHAR(100) 	NOT NULL,
	CONSTRAINT 			pk_ingredient_types PRIMARY KEY (ingredient_type)
);


CREATE TABLE ingredients (
	ingredient_id 		SERIAL 			NOT NULL,
	recipe_id 			INT4 			NOT NULL,
	display_order 		INT4			,
	ingredient_type 	INT4 			NOT NULL,
	sub_recipe_id 		INT4			,
	name 				VARCHAR(100) 	NOT NULL,
	qty					DECIMAL(10,5)	NOT NULL,
	unit_id 			INT4 			NOT NULL,
	CONSTRAINT 			pk_ingredients PRIMARY KEY (ingredient_id)
);


CREATE TABLE instructions (
	recipe_id 			INT4 			NOT NULL,
	step_num 			INT4 			NOT NULL,
	step_text 			VARCHAR(4096)
);


CREATE TABLE recipes (
	recipe_id 			SERIAL 			NOT NULL,
	name 				VARCHAR(1024) 	NOT NULL,
	yield_qty 			INT2			,
	yield_units 		VARCHAR(256)	,
	source 				VARCHAR(256) 	DEFAULT 'Unknown' 	NOT NULL,
	create_utime 		VARCHAR(20)  	NOT NULL,
	mod_utime 			VARCHAR(20)  	NOT NULL,
	author_user_id 		INT4			NOT NULL,
	CONSTRAINT 			pk_recipes PRIMARY KEY (recipe_id)
);


CREATE TABLE units (
	unit_id 			SERIAL 			NOT NULL,
	name 				VARCHAR(100) 	NOT NULL,
	abbreviation 		VARCHAR(10) 	NOT NULL,
	CONSTRAINT 			pk_units PRIMARY KEY (unit_id)
);


CREATE TABLE user_access_grants (
	user_id 			INT4 			NOT NULL,
	permission_id 		INT2 			NOT NULL,
	granter_user_id 	INT4 			NOT NULL,
	grant_utime			VARCHAR(20) 	NOT NULL
);


CREATE TABLE user_permissions (
	permission_id 		INT2 			NOT NULL,
	short_description 	VARCHAR(100) 	NOT NULL,
	long_description 	VARCHAR(1000)	,
	CONSTRAINT 			pk_user_permissions PRIMARY KEY (permission_id)
);


CREATE TABLE user_recipe_bookmarks (
	user_id 			INT4 			NOT NULL,
	recipe_id 			INT4 			NOT NULL,
	CONSTRAINT 			pk_user_recipe_bookmarks PRIMARY KEY (user_id, recipe_id)
);


CREATE TABLE users (
	user_id 			SERIAL 			NOT NULL,
	user_name 			VARCHAR(30) 	NOT NULL,
	user_name_lower 	VARCHAR(30) 	NOT NULL,
	password 			VARCHAR(40) 	NOT NULL,
	email 				VARCHAR(75) 	NOT NULL,
	url 				VARCHAR(100)	,
	status 				INT2 			DEFAULT 1 NOT NULL,
	email_private 		INT2			,
	create_utime 		VARCHAR(20)		NOT NULL,
	CONSTRAINT 			pk_users PRIMARY KEY (user_id),
	CONSTRAINT 			indx_unq_users_user_name_lower UNIQUE (user_name_lower)
);


CREATE TABLE login_log (
	user_id				INT4			NOT NULL,
	ip					VARCHAR(16)		,
	hostname			VARCHAR(255)	,
	login_utime			VARCHAR(20)		NOT NULL
);



------------------------
-- ADDITIONAL INDEXES --
------------------------

CREATE INDEX indx_login_log_user_id
	ON login_log (user_id);

CREATE INDEX indx_instructions_recipe_id
	ON instructions (recipe_id);

CREATE INDEX indx_ingredients_recipe_id
	ON ingredients (recipe_id);

CREATE INDEX indx_user_access_grants_uid
	ON user_access_grants (user_id);

CREATE INDEX indx_login_log_user_id
	ON login_log (user_id);

-----------------
-- CONSTRAINTS --
-----------------

ALTER TABLE category_entries
	ADD CONSTRAINT fk_cat_entries_category_id
	FOREIGN KEY (category_id)
	REFERENCES categories (category_id);

ALTER TABLE category_entries
	ADD CONSTRAINT fk_cat_entries_recipe_id
	FOREIGN KEY (recipe_id)
	REFERENCES recipes (recipe_id);

ALTER TABLE instructions
	ADD CONSTRAINT fk_instructions_recipe_id_type
	FOREIGN KEY (recipe_id)
	REFERENCES recipes (recipe_id);

ALTER TABLE ingredients
	ADD CONSTRAINT fk_ingredients_recipe_id
	FOREIGN KEY (recipe_id)
	REFERENCES recipes (recipe_id);

ALTER TABLE user_access_grants
	ADD CONSTRAINT fk_user_access_grants_g_uid
	FOREIGN KEY (granter_user_id)
	REFERENCES users (user_id);

ALTER TABLE user_access_grants
	ADD CONSTRAINT fk_user_access_grants_perm_id
	FOREIGN KEY (permission_id)
	REFERENCES user_permissions (permission_id);

ALTER TABLE user_access_grants
	ADD CONSTRAINT fk_user_access_grants_user_id
	FOREIGN KEY (user_id)
	REFERENCES users (user_id);

ALTER TABLE user_recipe_bookmarks
	ADD CONSTRAINT fk_user_recipe_bmarks_recipe_id
	FOREIGN KEY (recipe_id)
	REFERENCES recipes (recipe_id);

ALTER TABLE user_recipe_bookmarks
	ADD  CONSTRAINT fk_user_recipe_bookmarks_uid
	FOREIGN KEY (user_id)
	REFERENCES users (user_id);

ALTER TABLE login_log
	ADD CONSTRAINT fk_login_log_user_id
	FOREIGN KEY (user_id)
	REFERENCES users (user_id);


-- END tables-postgres.sql
