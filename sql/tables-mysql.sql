-- File:		tables-mysql.sql
-- Description:	DDL for ReciPants schema, MySQL version
-- Author:		Nick Grossman <nick@photondetector.com>
-- Tab stops:	4
-- Version:		1.2


------------
-- TABLES --
------------


CREATE TABLE categories (
	category_id 		INT4			NOT NULL AUTO_INCREMENT,
	parent 				INT4 			NOT NULL,
	name 				TEXT			NOT NULL,
	CONSTRAINT 			pk_categories PRIMARY KEY (category_id)
);


CREATE TABLE category_entries (
	recipe_id 			INT4 			NOT NULL,
	category_id			INT4 			NOT NULL,
	CONSTRAINT			pk_category_entries PRIMARY KEY (recipe_id, category_id)
);


CREATE TABLE ingredient_types (
	ingredient_type		INT4			NOT NULL AUTO_INCREMENT,
	name 				VARCHAR(100) 	NOT NULL,
	CONSTRAINT 			pk_ingredient_types PRIMARY KEY (ingredient_type)
);


CREATE TABLE ingredients (
	ingredient_id 		INT4			NOT NULL AUTO_INCREMENT,
	recipe_id 			INT4 			NOT NULL,
	display_order 		INT4			,
	ingredient_type 	INT4 			NOT NULL,
	sub_recipe_id 		INT4			,
	name 				VARCHAR(100) 	NOT NULL,
	qty					DECIMAL(10,5)	NOT NULL,
	unit_id 			INT4 			NOT NULL,
	CONSTRAINT 			pk_ingredients PRIMARY KEY (ingredient_id),
	INDEX				indx_ingredients_recipe_id (recipe_id)
);


CREATE TABLE instructions (
	recipe_id 			INT4 			NOT NULL,
	step_num 			INT4 			NOT NULL,
	step_text 			TEXT			,
	INDEX 				indx_instructions_recipe_id (recipe_id)
);


CREATE TABLE recipes (
	recipe_id 			INT4			NOT NULL AUTO_INCREMENT,
	name 				TEXT		 	NOT NULL,
	yield_qty 			INT2			,
	yield_units 		TEXT			,
	source 				TEXT			NOT NULL,
	create_utime 		VARCHAR(20)  	NOT NULL,
	mod_utime 			VARCHAR(20) 	NOT NULL,
	author_user_id 		INT4			NOT NULL,
	CONSTRAINT 			pk_recipes PRIMARY KEY (recipe_id)
);


CREATE TABLE units (
	unit_id 			INT4			NOT NULL AUTO_INCREMENT,
	name 				VARCHAR(100) 	NOT NULL,
	abbreviation 		VARCHAR(10) 	NOT NULL,
	CONSTRAINT 			pk_units PRIMARY KEY (unit_id)
);


CREATE TABLE user_access_grants (
	user_id 			INT4 			NOT NULL,
	permission_id 		INT2 			NOT NULL,
	granter_user_id 	INT4 			NOT NULL,
	grant_utime 		VARCHAR(20) 	NOT NULL,
	INDEX 				indx_user_access_grants_uid (user_id)
);


CREATE TABLE user_permissions (
	permission_id 		INT2 			NOT NULL,
	short_description 	VARCHAR(100) 	NOT NULL,
	long_description 	TEXT			,
	CONSTRAINT 			pk_user_permissions PRIMARY KEY (permission_id)
);


CREATE TABLE user_recipe_bookmarks (
	user_id 			INT4 			NOT NULL,
	recipe_id 			INT4 			NOT NULL,
	CONSTRAINT 			pk_user_recipe_bookmarks PRIMARY KEY (user_id, recipe_id)
);


CREATE TABLE users (
	user_id 			INT4			NOT NULL 		AUTO_INCREMENT,
	user_name 			VARCHAR(30) 	NOT NULL,
	user_name_lower 	VARCHAR(30) 	NOT NULL,
	password 			VARCHAR(40) 	NOT NULL,
	email 				VARCHAR(75) 	NOT NULL,
	url 				VARCHAR(100)	,
	status 				INT2 			DEFAULT 1 		NOT NULL,
	email_private 		INT2			,
	create_utime 		VARCHAR(20)		NOT NULL,
	CONSTRAINT 			pk_users PRIMARY KEY (user_id),
	CONSTRAINT 			indx_unq_users_user_name_lower UNIQUE (user_name_lower)
);


CREATE TABLE login_log (
	user_id				INT4			NOT NULL,
	ip					VARCHAR(16)		,
	hostname			VARCHAR(255)	,
	login_utime			VARCHAR(20)		NOT NULL,
	INDEX 				indx_login_log_user_id (user_id)
);



-----------------
-- CONSTRAINTS --
----------------- 

-- Not available in MySQL. You have been warned!


-- END tables-mysql.sql
