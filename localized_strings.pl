###########################################################################
# File      : localized_strings.pl
# Purpose   : Localized strings for programatically-generated messages.
# Program   : ReciPants ( http://recipants.photondetector.com/ )
# Version   : 1.2
# Author    : Nick Grossman <nick@photondetector.com>
# Tab stops : 4
#
# Copyright (c) 2002, 2003 Nicolai Grossman <nick@photondetector.com> and 
# contributors ( see http://recipants.photondetector.com/credits.html )
#
# This file is part of ReciPants.
#
# ReciPants is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# ReciPants is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with ReciPants; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
###########################################################################


# List of languages supported by the system.
@supported_languages = (
	"en"
);

# This maps supported language codes to language names. Used to generate
# the list of available languages.
%language_code_map = (
	'en' => 'English',
);


# NOTE: All hash names in this file should start with "ls_"
#       (for Localized String) to prevent naming conflicts.


##### common

%ls_must_be_signed_in = (
	en => 'You have to be singed in to do that!<BR><BR><B><A HREF="user.cgi?cmd=show_login">Sign In</A></B>',
	da => 'You have to be singed in to do that!<BR><BR><B><A HREF="user.cgi?cmd=show_login">Sign In</A></B>',
);

%ls_no_valid_command = (
	en => 'No valid command was supplied.',
	da => 'No valid command was supplied.',
);

%ls_no_category_id = (
	en => 'No category ID was supplied.',
	da => 'No category ID was supplied.',
);

%ls_invalid_numeric_format = (
	en => 'Invalid input format: must be numeric',
	da => 'Invalid input format: must be numeric',
);


##### category.cgi

%ls_no_subcategories_in_category = (
	en => 'There are no Subcategories in this Category',
	da => 'There are no Subcategories in this Category',
);

%ls_no_recipes_in_category = (
	en => 'There are no Recipes in this Category',
	da => 'There are no Recipes in this Category',
);

%ls_categories_title = (
	en => 'Categories',
	da => 'Kategorier',
);

%ls_category_tree_title = (
	en => 'Category Tree',
	da => 'Kategori Træ',
);


##### category_editor.cgi

%ls_category_editor_title = (
	en => 'Category Editor',
	da => 'Kategori Editor',
);

%ls_no_parent_category_id = (
	en => 'No parent category ID was supplied.',
	da => 'No parent category ID was supplied.',
);

%ls_no_perm_edit_categories = (
	en => 'You don\'t have permission to edit Categories.',
	da => 'You don\'t have permission to edit Categories.',
);

%ls_missed_name_field = (
	en => 'You missed the <B>Name</B> field. Please fill it in.',
	da => 'You missed the <B>Name</B> field. Please fill it in.',
);

%ls_category_added = (
	en => 'Category added!',
	da => 'Kategori added!',
);

%ls_category_renamed = (
	en => 'Category renamed!',
	da => 'Kategori renamed!',
);

%ls_category_moved = (
	en => 'Category moved!',
	da => 'Kategori flyttet!',
);

%ls_category_deleted = (
	en => 'Category deleted!',
	da => 'Kategori fjernet!',
);

%ls_cant_delete_root_category = (
	en => 'Sorry, but you can\'t delete the master root category (category 0).',
	da => 'Sorry, but you can\'t delete the master root category (category 0).',
);

%ls_cant_move_category_under_child = (
	en => 'Sorry, you can\'t move a category under one of its children.',
	da => 'Sorry, you can\'t move a category under one of its children.',
);

%ls_cant_get_new_category_id = (
	en => 'Can\'t get new category ID.',
	da => 'Can\'t get new category ID.',
);

##### librecipants.pl

%ls_bad_cookie = (
	en => 'Cookie authentication failed! Nice try!',
	da => 'Cookie authentication failed! Nice try!',
);

%ls_no_matching_users = (
	en => 'No matching users were found.',
	da => 'Brugere kan ikke findes.',
);

%ls_edit_categories = (
	en => 'Edit Categories',
	da => 'Edit Kategorier',
);

%ls_edit_user = (
	en => 'Edit User: ',
	da => 'Edit Bruger: ',
);

%ls_edit_users = (
	en => 'Edit Users',
	da => 'Edit Brugerer',
);

%ls_view_system_info = (
	en => 'System Information',
	da => 'Systeminformation',
);

%ls_cant_connect_to_database = (
	en => 'Can\'t connect to database: ',
	da => 'Can\'t connect to database: ',
);

%ls_cant_prepare_sql = (
	en => 'Can\'t prepare SQL statement: ',
	da => 'Can\'t prepare SQL statement: ',
);

%ls_cant_execute_sql = (
	en => 'Can\'t execute SQL statement: ',
	da => 'Can\'t execute SQL statement: ',
);

%ls_cant_find_recipe = (
	en => 'Can\'t find the specified recipe.',
	da => 'Opskrift can ikke findes.',
);

%ls_recipe_in_no_categories = (
	en => 'This recipe is not in any categories.',
	da => 'Denne opskrift er ikke i nogle kategorier.',
);

%ls_cant_get_template = (
	en => 'ERROR: Can\'t get template file ',
	da => 'FEJL: Can\'t get template file ',
);

%ls_unknown_error = (
	en => 'Something went wrong, but I have no idea what happened.',
	da => 'Something went wrong, but I have no idea what happened.',
);

%ls_unknown_sucess = (
	en => 'Whatever your were trying to do worked!',
	da => 'Whatever your were trying to do worked!',
);

%ls_success_title = (
	en => 'Nice!',
	da => 'Fedt!',
);

%ls_error_title = (
	en => 'Crapcakes!',
	da => 'Oops!',
);

%ls_no_email_method_defined = (
	en => 'Email configuration error: No sending method defined.',
	da => 'Email configuration error: No sending method defined.',
);

%ls_cant_open_pipe_to = (
	en => 'Can\'t open pipe to',
	da => 'Can\'t open pipe to',
);

##### recipe.cgi

%ls_no_recipe_id = (
	en => 'No recipe ID was supplied.',
	da => 'No recipe ID was supplied.',
);

%ls_word_recipe = (
	en => 'Recipe',
	da => 'Opskrift',
);

%ls_word_scaled = (
	en => 'Scaled',
	da => 'Scaled',
);

%ls_word_unknown = (
	en => 'Unknown',
	da => 'Unknown',
);

%ls_edit_this_recipe = (
	en => 'Edit This Recipe',
	da => 'Edit Denne Opskrift',
);

%ls_delete_this_recipe = (
	en => 'Delete This Recipe',
	da => 'Delete Denne Opskrift',
);

%ls_delete_recipe_confirm_js = (
	en => 'Are you sure you want to permanently delete this recipe? There is no way to get it back!',
	da => 'Are you sure you want to permanently delete this recipe? There is no way to get it back!',
);

%ls_cant_open_export_file = (
	en => 'Could not open export file ',
	da => 'Could not open export file ',
);

%ls_mm_qty_field_too_long = (
	en => 'This recipe can\'t be exported to Meal-Master because a quantity field is too long.',
	da => 'This recipe can\'t be exported to Meal-Master because a quantity field is too long.',
);

%ls_email_recipe_subject = (
	en => 'Recipe: ',
	da => 'Opskrift: ',
);

%ls_email_recipe_success = (
	en => 'The recipe has been sent to ',
	da => 'The recipe has been sent to ',
);

%ls_no_message = (
	en => '(No message)',
	da => '(No message)',
);


##### recipe_editor.cgi

%ls_bad_ingredient_format = (
	en => 'Looks like a bad ingredient format. Please check the <B>Ingredients</B> box.',
	da => 'Looks like a bad ingredient format. Please check the <B>Ingredients</B> box.',
);

%ls_add_new_recipe = (
	en => 'Add New Recipe',
	da => 'Adder Nye Opskrift',
);

%ls_cant_edit_recipe_not_owner = (
	en => 'You don\'t have permission to edit recipes that you didn\'t enter.',
	da => 'You don\'t have permission to edit recipes that you didn\'t enter.',
);

%ls_edit_recipe = (
	en => 'Edit Recipe: ',
	da => 'Edit Opskrift: ',
);

%ls_recipe_name = (
	en => 'Recipe Name',
	da => 'Opskrift Navn',
);

%ls_ingredients = (
	en => 'Ingredients',
	da => 'Ingredienser',
);

%ls_instructions = (
	en => 'Instructions',
	da => 'Fremgangsmåder',
);

%ls_yield_quantity = (
	en => 'Yield Quantity',
	da => 'Yield Quantity',
);

%ls_yield_units = (
	en => 'Yield Units',
	da => 'Yield Units',
);

%ls_box = (
	en => 'box',
	da => 'box',
);

%ls_boxes = (
	en => 'boxes',
	da => 'boxer',
);

%ls_you_missed_the = (
	en => 'You missed the',
	da => 'Du har glemt den',
);

%ls_recipe_saved = (
	en => 'Recipe saved!',
	da => 'Opskrift gemt!',
);

%ls_cant_get_new_recipe_id = (
	en => 'Can\'t get new recipe ID!',
	da => 'Can\'t get new recipe ID!',
);

%ls_check_ingredients_box = (
	en => 'Please check the <B>Ingredients</B> box.',
	da => 'Please check the <B>Ingredients</B> box.',
);

%ls_the_unit = (
	en => 'The unit',
	da => 'The unit',
);

%ls_doesnt_exist = (
	en => 'doesn\'t exist',
	da => 'eksistere ikke',
);

%ls_instructions_for_step = (
	en => 'Instructions for step ',
	da => 'Instructioner til step ',
);

%ls_are_too_long = (
	en => ' are too long.',
	da => ' er for langt.',
);

%ls_no_delete_recipe_perm = (
	en => 'You don\'t have permission to delete recipes.',
	da => 'You don\'t have permission to delete recipes.',
);

%ls_recipe_deleted = (
	en => 'Recipe deleted.',
	da => 'Opskrift fjernet.',
);

%ls_recipe_saved_success_title = (
	en => 'Recipe Saved!',
	da => 'Opskrift Gemt!',
);

%ls_set_autocommit_off_failed = (
	en => 'Can\'t turn off Auto-Commit in the database.',
	da => 'Can\'t turn off Auto-Commit in the database.',
);



##### recipe_search.cgi

%ls_search_results_for = (
	en => 'Search Results for ',
	da => 'Søgeresultater for ',
);

%ls_no_search_term = (
	en => 'Please enter something to search for.',
	da => 'Indtast et eller flere ord i søgefeltet.',
);

%ls_no_recipe_name_matches = (
	en => 'No matching recipe names were found.',
	da => 'Ingen resultater fundet i Opskrift Navner.',
);

%ls_no_ingredient_matches = (
	en => 'No matching ingredients were found.',
	da => 'Ingen resultater fundet i Ingredienser.',
);

%ls_no_instruction_matches = (
	en => 'No matching instructions were found.',
	da => 'Ingen resultater findet i Framgangsmåder.',
);

%ls_advanced_search_title = (
	en => 'Advanced Search',
	da => 'Avanceret Søgning',
);

%ls_less_than = (
	en => '(less than)',
	da => '(less than)',
);

%ls_greater_than = (
	en => '(greater than)',
	da => '(greater than)',
);


##### user.cgi

%ls_email_private = (
	en => '&lt;private&gt;',
	da => '&lt;privat&gt;',
);

%ls_no_user_id = (
	en => 'No user ID was supplied.',
	da => 'No user ID was supplied.',
);

%ls_already_signed_in_as = (
	en => 'You\'re already signed in as',
	da => 'You\'re already signed in as',
);

%ls_need_uname_and_passwd = (
	en => 'You must fill in both your user name and your password.',
	da => 'You must fill in both your user name and your password.',
);

%ls_login_auth_failed = (
	en => 'Sorry, please try again.',
	da => 'Prøve igen.',
);

%ls_account_inactive = (
	en => 'Sorry, this account is not active.',
	da => 'Sorry, this account is not active.',
);

%ls_signed_in = (
	en => 'signed in!',
	da => 'signed in!',
);

%ls_signed_out = (
	en => 'signed out!',
	da => 'signed out!',
);

%ls_cant_log_out_not_logged_in = (
	en => 'I can\'t log you out because you aren\'t logged in!',
	da => 'I can\'t log you out because you aren\'t logged in!',
);

%ls_already_logged_in_as = (
	en => 'You\'re already signed in as ',
	da => 'Du er allerede logged in som ',
);

%ls_sign_in_title = (
	en => 'Sign In',
	da => 'Login',
);

%ls_missing_uname_and_email = (
	en => 'You must fill out both the Username and Email fields.',
	da => 'You must fill out both the Username and Email fields.',
);

%ls_email_too_long = (
	en => 'You need a shorter email address!',
	da => 'Din email adresse er for langt!',
);

%ls_bad_email_format = (
	en => 'It looks like there\'s a problem with your Email address. Please check it.',
	da => 'It looks like there\'s a problem with your Email address. Please check it.',
);

%ls_uname_too_long = (
	en => 'Your username is too long. Please choose a shorter one.',
	da => 'Din brugernavn er for langt!',
);

%ls_uname_taken = (
	en => 'Sorry, that Username is already taken. Please choose another one.',
	da => 'Sorry, that Username is already taken. Please choose another one.',
);

%ls_email_already_in_use = (
	en => 'That email address is already in use!',
	da => 'That email address is already in use!',
);

%ls_welcome_email_subject = (
	en => 'Your ReciPants account information',
	da => 'Your ReciPants account information',
);

%ls_create_account_success = (
	en => 'Your account has been created!<BR><BR>You should receive an email with your password in the next few minutes.',
	da => 'Your account has been created!<BR><BR>You should receive an email with your password in the next few minutes.',
);

%ls_cant_get_new_user_id = (
	en => 'Can\'t get new user ID!',
	da => 'Can\'t get new user ID!',
);

%ls_change_passwd_title = (
	en => 'Change My Password',
	da => 'Change My Password',
);

%ls_fill_in_all_fields = (
	en => 'You must fill in all of the fields.',
	da => 'You must fill in all of the fields.',
);

%ls_new_passwds_dont_match = (
	en => 'Your new passwords don\'t match. Please try again.',
	da => 'Your new passwords don\'t match. Please try again.',
);

%ls_bad_passwd_length = (
	en => 'Your new password must be between 6 and 20 characters in length. Please choose a different one.',
	da => 'Your new password must be between 6 and 20 characters in length. Please choose a different one.',
);

%ls_bad_current_passwd = (
	en => 'Your current password is incorrect. Please try again.',
	da => 'Din password er forkert. Gærne prøv igen.',
);

%ls_passwd_change_success = (
	en => 'Your password has been changed!',
	da => 'Your password has been changed!',
);

%ls_missing_email = (
	en => 'You must fill in your email address.',
	da => 'You must fill in your email address.',
);

%ls_no_account_match_for_email = (
	en => 'Sorry, but I can\'t find an account for your email address.',
	da => 'Sorry, but I can\'t find an account for your email address.',
);

%ls_passwd_reminder_email_subject = (
	en => 'ReciPants account information reminder',
	da => 'ReciPants account information reminder',
);

%ls_passwd_reminder_success = (
	en => 'Your account information has been emailed to you. You should receive it in the next few minutes.',
	da => 'Your account information has been emailed to you. You should receive it in the next few minutes.',
);

%ls_send_passwd_title = (
	en => 'Send My Password',
	da => 'Send My Password',
);

%ls_none = (
	en => 'none',
	da => 'ingen',
);

%ls_profile_for = (
	en => 'Profile for ',
	da => 'Profil for ',
);

%ls_missing_language_code = (
	en => 'No language code was supplied.',
	da => 'Jeg mangler en sprog kode.',
);

%ls_language_set_success_title = (
	en => 'Language saved!',
	da => 'Sprog gemt!',
);

%ls_language_not_found = (
	en => 'Language not found.',
	da => 'Sprog kan ikke findes.',
);

%ls_change_info_title = (
	en => 'Change My Info',
	da => 'Change My Info',
);

%ls_save_info_success = (
	en => 'Your info has been saved!',
	da => 'Brugerinformation gemt!',
);

%ls_recipe_bookmarks_title = (
	en => 'Favorite Recipes',
	da => 'Favorit Opskrifter',
);

%ls_add_recipe_bookmark_success = (
	en => 'Recipe bookmark added!',
	da => 'Opskrift bookmark gemt!',
);

%ls_delete_recipe_bookmark_success = (
	en => 'Recipe bookmark deleted!',
	da => 'Recipe bookmark deleted!',
);

%ls_no_recipe_bookmarks = (
	en => 'no recipe bookmarks',
	da => 'Recipe bookmark deleted!',
);


##### user_editor.cgi

%ls_user_editor_search_title = (
	en => 'User Editor: Search',
	da => 'User Editor: Search',
);

%ls_word_yes = (
	en => 'Yes',
	da => 'Ja',
);

%ls_word_no = (
	en => 'No',
	da => 'Nej',
);

%ls_no_perm_edit_users = (
	en => 'You don\'t have permission to edit users.',
	da => 'You don\'t have permission to edit users.',
);

%ls_user_not_found = (
	en => 'User not found!',
	da => 'Bruger kan ikke findes!',
);

%ls_missing_user_name = (
	en => 'Please fill in the Username field.',
	da => 'Please fill in the Username field.',
);

%ls_missing_email = (
	en => 'Please fill in the Email field.',
	da => 'Please fill in the Email field.',
);


##### stats.cgi

%ls_no_perm_stats = (
	en => 'You don\'t have permission to view system information.',
	da => 'You don\'t have permission to view system information.',
);

%ls_system_stats_title = (
	en => 'System Information',
	da => 'Systeminformation',
);


##### utility.cgi

%ls_temperature_converter = (
	en => 'Temperature Converter',
	da => 'Temperature Converter',
);

%ls_sweetness_converter = (
	en => 'Sweetness Converter',
	da => 'Sweetness Converter',
);


##### cart.cgi

%ls_no_valid_destination = (
	en => 'I don\'t know where to put this!',
	da => 'I don\'t know where to put this!',
);



# All done! Return true (DO NOT REMOVE)
1;

# END localized_strings.pl
