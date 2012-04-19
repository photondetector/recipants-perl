-- File:		drop_all_tables.sql
-- Description:	Drops all ReciPants tables - THIS WILL DELETE ALL OF YOUR
--              ReciPants DATA!
-- Author:		Nick Grossman <nick@photondetector.com>
-- Tab stops:	4
-- Version:		1.0
--
-- REVISION HISTORY
-- v1.0 		20 Sept 2003 - Initial version


DROP TABLE categories;
DROP TABLE category_entries;
DROP TABLE ingredient_types;
DROP TABLE ingredients;
DROP TABLE instructions;
DROP TABLE recipes;
DROP TABLE units;
DROP TABLE user_access_grants;
DROP TABLE user_permissions;
DROP TABLE user_recipe_bookmarks;
DROP TABLE users;
DROP TABLE login_log;

-- END

