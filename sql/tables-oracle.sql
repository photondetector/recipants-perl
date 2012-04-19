-- File:		tables_oracle.sql
-- Description:	DDL for ReciPants schema, Oracle version
-- Author:		Nick Grossman <nick@photondetector.com>
-- Tab stops:	4
-- Version:		1.2


------------
-- TABLES --
------------


CREATE TABLE categories (
	category_id 		NUMBER(5)		NOT NULL,
	parent 				NUMBER(5) 		NOT NULL,
	name 				VARCHAR2(256)	NOT NULL,
	CONSTRAINT 			pk_categories PRIMARY KEY (category_id) USING INDEX
) CACHE;


CREATE TABLE category_entries (
	recipe_id 			NUMBER(5) 		NOT NULL,
	category_id			NUMBER(5) 		NOT NULL,
	CONSTRAINT			pk_category_entries PRIMARY KEY (recipe_id, category_id) USING INDEX
);


CREATE TABLE ingredient_types (
	ingredient_type		NUMBER(5)		NOT NULL,
	name 				VARCHAR2(100) 	NOT NULL,
	CONSTRAINT 			pk_ingredient_types PRIMARY KEY (ingredient_type) USING INDEX
) CACHE;


CREATE TABLE ingredients (
	ingredient_id 		NUMBER(5) 		NOT NULL,
	recipe_id 			NUMBER(5) 		NOT NULL,
	display_order 		NUMBER(5)		,
	ingredient_type 	NUMBER(5) 		NOT NULL,
	sub_recipe_id 		NUMBER(5)		,
	name 				VARCHAR2(100) 	NOT NULL,
	qty 				NUMERIC			NOT NULL,
	unit_id 			NUMBER(5) 		NOT NULL,
	CONSTRAINT 			pk_ingredients PRIMARY KEY (ingredient_id) USING INDEX
);


CREATE TABLE instructions (
	recipe_id 			NUMBER(5) 		NOT NULL,
	step_num 			NUMBER(5) 		NOT NULL,
	step_text 			VARCHAR2(4000)
);


CREATE TABLE recipes (
	recipe_id 			NUMBER(5) 		NOT NULL,
	name 				VARCHAR2(1024) 	NOT NULL,
	yield_qty 			NUMBER(3)		,
	yield_units 		VARCHAR2(256)	,
	source 				VARCHAR2(256) 	DEFAULT 'Unknown' 	NOT NULL,
	create_utime 		VARCHAR2(20)  	NOT NULL,
	mod_utime 			VARCHAR2(20)  	NOT NULL,
	author_user_id 		NUMBER(5)		NOT NULL,
	CONSTRAINT 			pk_recipes PRIMARY KEY (recipe_id) USING INDEX
);


CREATE TABLE units (
	unit_id 			NUMBER(5) 		NOT NULL,
	name 				VARCHAR2(100) 	NOT NULL,
	abbreviation 		VARCHAR2(10) 	NOT NULL,
	CONSTRAINT 			pk_units PRIMARY KEY (unit_id) USING INDEX
) CACHE;


CREATE TABLE user_access_grants (
	user_id 			NUMBER(5) 		NOT NULL,
	permission_id 		NUMBER(4) 		NOT NULL,
	granter_user_id 	NUMBER(5) 		NOT NULL,
	grant_utime			VARCHAR2(20) 	NOT NULL
);


CREATE TABLE user_permissions (
	permission_id 		NUMBER(4) 		NOT NULL,
	short_description 	VARCHAR2(100) 	NOT NULL,
	long_description 	VARCHAR2(1000)	,
	CONSTRAINT 			pk_user_permissions PRIMARY KEY (permission_id) USING INDEX
) CACHE;


CREATE TABLE user_recipe_bookmarks (
	user_id 			NUMBER(5) 		NOT NULL,
	recipe_id 			NUMBER(5) 		NOT NULL,
	CONSTRAINT 			pk_user_recipe_bookmarks PRIMARY KEY (user_id, recipe_id) USING INDEX
);


CREATE TABLE users (
	user_id 			NUMBER(5)		NOT NULL,
	user_name 			VARCHAR2(30) 	NOT NULL,
	user_name_lower 	VARCHAR2(30) 	NOT NULL,
	password 			VARCHAR2(40) 	NOT NULL,
	email 				VARCHAR2(75) 	NOT NULL,
	url 				VARCHAR2(100)	,
	status 				NUMBER(4) 		DEFAULT 1 NOT NULL,
	email_private 		NUMBER(4)		,
	create_utime 		VARCHAR2(20)	NOT NULL,
	CONSTRAINT 			pk_users PRIMARY KEY (user_id) USING INDEX,
	CONSTRAINT 			indx_unq_users_user_name_lower UNIQUE (user_name_lower)
);


CREATE TABLE login_log (
	user_id				NUMBER(5)		NOT NULL,
	ip					VARCHAR2(16)	,
	hostname			VARCHAR2(255)	,
	login_utime			VARCHAR2(20)	NOT NULL
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
	ADD CONSTRAINT fk_user_recipe_bmks_recipe_id
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




-- The following is for auto-incrementing IDs as Oracle has no appropriate types

---------------
-- SEQUENCES --
---------------

CREATE SEQUENCE seq_categories_category_id
	MINVALUE 0
	START WITH 0
	INCREMENT BY 1
	NOCYCLE;

CREATE SEQUENCE seq_recipes_recipe_id
	MINVALUE 0
	START WITH 0
	INCREMENT BY 1
	NOCYCLE;

CREATE SEQUENCE seq_units_unit_id
	MINVALUE 0
	START WITH 0
	INCREMENT BY 1
	NOCYCLE;

CREATE SEQUENCE seq_users_user_id
	MINVALUE 1
	START WITH 1
	INCREMENT BY 1
	NOCYCLE;



--------------
-- TRIGGERS --
--------------

CREATE OR REPLACE TRIGGER t_bri_categories
	BEFORE INSERT ON categories
	FOR EACH ROW
BEGIN
	SELECT seq_categories_category_id.NEXTVAL
		INTO :new.category_id
		FROM dual;
END;
/


CREATE OR REPLACE TRIGGER t_bri_units
	BEFORE INSERT ON units
	FOR EACH ROW
BEGIN
	SELECT seq_units_unit_id.NEXTVAL
		INTO :new.unit_id
		FROM dual;
END;
/


-- Note that there are no triggers for USERS or RECIPES. The program
-- needs the new IDs back immediately so it gets them from the sequences
-- manually and inserts them itself.


-- END tables-oracle.sql
