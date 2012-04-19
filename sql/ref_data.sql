-- File:		ref_data.sql
-- Description:	Reference data for recipe manager lookup tables
-- Author:		Nick Grossman <nick@photondetector.com>
-- Tab stops:	4
-- Version:		1.0.1


-- Unit codes
INSERT INTO units (name, abbreviation) VALUES ('Teaspoons', 	'tsp');
INSERT INTO units (name, abbreviation) VALUES ('Tablespoons', 	'TBSP');
INSERT INTO units (name, abbreviation) VALUES ('Cups', 			'c');
INSERT INTO units (name, abbreviation) VALUES ('Pints', 		'pt');
INSERT INTO units (name, abbreviation) VALUES ('Quarts', 		'qt');
INSERT INTO units (name, abbreviation) VALUES ('Gallons', 		'gal');
INSERT INTO units (name, abbreviation) VALUES ('Mililiters', 	'ml');
INSERT INTO units (name, abbreviation) VALUES ('Liters', 		'l');
INSERT INTO units (name, abbreviation) VALUES ('Ounces', 		'oz');
INSERT INTO units (name, abbreviation) VALUES ('Fluid ounces', 	'Fl oz');
INSERT INTO units (name, abbreviation) VALUES ('Grams', 		'g');
INSERT INTO units (name, abbreviation) VALUES ('Kilograms', 	'kg');
INSERT INTO units (name, abbreviation) VALUES ('Pinches', 		'pinches');
INSERT INTO units (name, abbreviation) VALUES ('Each', 			'ea');


-- Ingredient type codes
INSERT INTO ingredient_types (ingredient_type, name) VALUES (1, 'Normal');
INSERT INTO ingredient_types (ingredient_type, name) VALUES (2, 'Sub-heading');
INSERT INTO ingredient_types (ingredient_type, name) VALUES (3, 'Divider');
INSERT INTO ingredient_types (ingredient_type, name) VALUES (4, 'Recipe Link');


-- User permission codes
INSERT INTO user_permissions (permission_id, short_description, long_description) VALUES (0, 'All Access',        'User may do anything possible in the system (root access). If a user has All Access permission, is is not necessary to grant them anything else.');
INSERT INTO user_permissions (permission_id, short_description, long_description) VALUES (1, 'Delete Any Recipe', 'User may delete any recipe in the system.');
INSERT INTO user_permissions (permission_id, short_description, long_description) VALUES (2, 'Edit Any Recipe',   'User may make changes to any recipe in the system.');
INSERT INTO user_permissions (permission_id, short_description, long_description) VALUES (3, 'Edit Any Category', 'User may edit (Create, Rename, Move, Delete) any Category in the system.');


-- Master category
INSERT INTO categories (category_id, parent, name) VALUES ('0', '-1', 'All Categories');


-- Administrator user account info
INSERT INTO users (user_name, user_name_lower, password, email, create_utime) VALUES ('admin', 'admin', 'change_me', 'change_me', '1064093171');
INSERT INTO user_access_grants (user_id, permission_id, granter_user_id, grant_utime) VALUES (1, 0, 1, '1064093171');


-- END ref_data.sql
