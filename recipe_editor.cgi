#!/usr/bin/perl

###########################################################################
# File      : recipe_editor.cgi
# Program   : ReciPants ( http://recipants.photondetector.com/ )
# Purpose	: Handles recipe creation and editing.
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

use Math::Fraction;
require "librecipants.pl";

# _____ GLOBAL VARIABLES ____________________________________________

$output;
$cmd       = param('cmd');
$recipe_id = param('recipe_id');

# _____ END GLOBAL VARIABLES ________________________________________


&InitUser();

if(! $logged_in) {
	&PrintErrorExit($ls_must_be_signed_in{$language});
}

# Make sure we have all necessary args.
if(! $cmd || (
	$cmd ne "new"			&& $cmd ne "delete"		&& 
	$cmd ne "save_edited"	&& $cmd ne "save_new"	&&
	$cmd ne "edit"
	))
{
	&PrintErrorExit($ls_no_valid_command{$language});
} 


# We need a recipe ID for everything except adding a new recipe and
# showing the new recipe form
if($cmd ne "new" && $cmd ne "save_new") {
	# Bail if no ID
	unless($recipe_id) {
		&PrintErrorExit($ls_no_recipe_id{$language});
	}

	# Enforce numeric format
	unless($recipe_id =~ /^\d+$/) {
		&PrintErrorExit($ls_invalid_numeric_format{$language});
	}

}

# We've got a legit command and a recipe_id (if necessary), so set up the template
$output = &GetTemplate("recipe_edit.html");
$output =~ s/REP_RECIPE_ID/$recipe_id/g;

if($cmd eq "new") {
	&NewRecipeScreen();
}
elsif($cmd eq "edit") {
	&EditRecipeScreen($recipe_id);
}
elsif($cmd eq "save_new" || $cmd eq "save_edited") {
	&SaveRecipe($recipe_id);
}
elsif($cmd eq "delete") {
	&DeleteRecipe($recipe_id);
}

&CleanExit(0);


# _____ FUNCTIONS ___________________________________________________

#####################################################################
# NewRecipeScreen()
#
# Displays the add recipe screen (blanked out edit recipe template)
#####################################################################
sub NewRecipeScreen() {
	my($category_tree) = &GetCategoryTreeCheckboxes();

	$output =~ s/REP_PAGE_TITLE/Add New Recipe/g;
	$output =~ s/REP_CGI_CMD/save_new/g;
	$output =~ s/REP_NAME//g;
	$output =~ s/REP_RECIPE_ID//g;
	$output =~ s/REP_INGREDIENTS//g;
	$output =~ s/REP_INSTRUCTIONS//g;
	$output =~ s/REP_YIELD_QTY//g;
	$output =~ s/REP_YIELD_UNITS//g;
	$output =~ s/REP_SOURCE//g;
	$output =~ s/REP_CATEGORY_TREE/$category_tree/g;
	$output =~ s/REP_ERROR_MESSAGE//g;
	&ShowPage($ls_add_new_recipe{$language}, $output);
}


#####################################################################
# EditRecipeScreen($recipe_id)
#
# Displays the edit recipe screen for recipe recipe_id.
#####################################################################
sub EditRecipeScreen() {
	my($l_recipe_id) = @_;
	my(%base_info, @ingredients, $ingredients_formatted, @instructions,
		$instructions_formatted, @categories, $categories_formatted,
		$category_id);

	$base_info = &GetRecipeBaseInfo($l_recipe_id);

	# Verify access
	unless(	&UserHasPermission($user_id, $perm_edit_any_recipe) ||
			$base_info->{'author_user_id'} == $user_id)
	{
		&PrintErrorExit($ls_cant_edit_recipe_not_owner{$language});
	}

	@ingredients  = &GetRecipeIngredients($l_recipe_id);
	@instructions = &GetRecipeInstructions($l_recipe_id);
	@categories   = &GetCategoriesForRecipe($l_recipe_id);

	# Format ingredients and instructions for output
	foreach(@instructions) {
		$instructions_formatted .= $_ . "\n";
	}

	for $i (0 .. $#ingredients) {
		$ingredients_formatted .= 
			$ingredients[$i]->{'name'}         . "\*" . 
			$ingredients[$i]->{'qty'}          . "\*" .
			$ingredients[$i]->{'abbreviation'} . "\n";
	}

	# Categories
	$categories_formatted = &GetCategoryTreeCheckboxes();
	foreach $category_id (@categories) {
		$categories_formatted =~ s/VALUE=\"$category_id\"/VALUE=\"$category_id\" CHECKED/g;
	}

	# Populate and print the output template
	$output =~ s/REP_PAGE_TITLE/Edit Recipe\: $base_info->{'name'}/g;
	$output =~ s/REP_CGI_CMD/save_edited/g;
	$output =~ s/REP_NAME/$base_info->{'name'}/g;
	$output =~ s/REP_INGREDIENTS/$ingredients_formatted/g;
	$output =~ s/REP_INSTRUCTIONS/$instructions_formatted/g;
	$output =~ s/REP_YIELD_QTY/$base_info->{'yield_qty'}/g;
	$output =~ s/REP_YIELD_UNITS/$base_info->{'yield_units'}/g;
	$output =~ s/REP_SOURCE/$base_info->{'source'}/g;
	$output =~ s/REP_CATEGORY_TREE/$categories_formatted/g;
	$output =~ s/REP_ERROR_MESSAGE//g;
	&ShowPage($ls_edit_recipe{$language} . $base_info->{'name'}, $output);
}


#####################################################################
# EditRecipeScreenError($error_message)
#
# Displays the edit recipe screen filled out with submitted values
# and an error message.
#####################################################################
sub EditRecipeScreenError() {
	my($error_message) = @_;
	my($error_box, $page_title, $name, $ingredients, $instructions,
		$yield_qty, $yield_units, $source, @categories, $categories_formatted);

	# Roll back transaction
#	$dbh->rollback();

	# Yeah, yeah... RTFM for CGI.pm and figure out how to get a hash
	$name         = param('name');
	$ingredients  = param('ingredients');
	$instructions = param('instructions');
	$yield_qty    = param('yield_qty');
	$yield_units  = param('yield_units');
	$source       = param('source');
	@categories   = param('categories');

	# Set page title
	if($cmd eq "save_edited") {
		$page_title = $ls_edit_recipe{$language} . $name;
	} else {
		$page_title = $ls_add_new_recipe{$language};
	}

	# Get error template and fill it out
	$error_box = &GetTemplate("error_box.html");
	$error_box =~ s/REP_MESSAGE/$error_message/g;

	# Handle categories
	$categories_formatted = &GetCategoryTreeCheckboxes();
	foreach $category_id (@categories) {
		$categories_formatted =~ s/VALUE=\"$category_id\"/VALUE=\"$category_id\" CHECKED/g;
	}

	# Fill out the rest of the normal form w/ supplied values
	$output =~ s/REP_ERROR_MESSAGE/$error_box/g;
	$output =~ s/REP_PAGE_TITLE/$page_title/g;
	$output =~ s/REP_CGI_CMD/$cmd/g;
	$output =~ s/REP_NAME/$name/g;
	$output =~ s/REP_RECIPE_ID/$recipe_id/g;
	$output =~ s/REP_INGREDIENTS/$ingredients/g;
	$output =~ s/REP_INSTRUCTIONS/$instructions/g;
	$output =~ s/REP_YIELD_QTY/$yield_qty/g;
	$output =~ s/REP_YIELD_UNITS/$yield_units/g;
	$output =~ s/REP_SOURCE/$source/g;
	$output =~ s/REP_CATEGORY_TREE/$categories_formatted/g;

	&ShowPage($page_title, $output);

	&CleanExit(0);
}


#####################################################################
# SaveRecipe($recipe_id)
#
# Saves (creates or updates) a recipe to the database.
#####################################################################
sub SaveRecipe() {
	my($l_recipe_id) = @_;
	my($new_recipe_id, @missing_fields, $missing_fields_formatted, $ctr,
		$name, $ingredients, $instructions, $yield_qty, $yield_units,
		$source, @categories, %base_info, $output);

	# Do edit access check if we're saving an existing recipe
	if($l_recipe_id) {
		%base_info = &GetRecipeBaseInfo($l_recipe_id);

		unless(	&UserHasPermission($user_id, $perm_edit_any_recipe) ||
				$base_info->{'author_user_id'} != $user_id)
		{
			&PrintErrorExit($ls_cant_edit_recipe_not_owner{$language});
		}
	}

	# Get args and clean them up
	$name         = &DBEscapeString(&trim(param('name')));
	$ingredients  = &DBEscapeString(&trim(param('ingredients')));
	$instructions = &DBEscapeString(&trim(param('instructions')));
	$yield_qty    = &DBEscapeString(&trim(param('yield_qty')));
	$yield_units  = &DBEscapeString(&trim(param('yield_units')));
	$source       = &DBEscapeString(&trim(param('source')));
	@categories   = param('categories');

	# Validate the categories as having numeric values
	foreach $category (@categories) {
	    unless($category =~ /^\d+$/) {
			&PrintErrorExit($ls_invalid_numeric_format{$language});
	    }
	}

	# Check for required args (source & categories are not required)
	if($name         eq "") { push(@missing_fields, $ls_recipe_name{$language}); }
	if($ingredients  eq "") { push(@missing_fields, $ls_ingredients{$language}); }
	if($instructions eq "") { push(@missing_fields, $ls_instructions{$language}); }
	if($yield_qty    eq "") { push(@missing_fields, $ls_yield_quantity{$language}); }
	if($yield_units  eq "") { push(@missing_fields, $ls_yield_units{$language}); }

	# If anything is missing, build an error string and bail
	if(length($missing_fields[0]) != 0) {
		$ctr = 0;

		while($ctr <= $#missing_fields) {
			# I'm sure there's a smarter way to do this, but I don't care right now
			if($ctr < $#missing_fields) {		# Not last
				$missing_fields_formatted .= $missing_fields[$ctr]; # Add entry

				if(($ctr <= ($#missing_fields -1)) && ($#missing_fields != 1)) {
					$missing_fields_formatted .= ",";
				}

				$missing_fields_formatted .= " ";
			} elsif($#missing_fields > 0) {		# Last and > 1 missing field
				$missing_fields_formatted .= "</B> and <B>$missing_fields[$ctr]";
			} else {							# The only field
				$missing_fields_formatted .= $missing_fields[$ctr];
			}

			$ctr++;
		}
	
		# Handle plurals
		if($#missing_fields >= 1) {
			$missing_fields_formatted .= "</B> " . $ls_boxes{$language};
		} else {
			$missing_fields_formatted .= "</B> " . $ls_box{$language};
		}

		&EditRecipeScreenError($ls_you_missed_the{$language} . 
			" <B>$missing_fields_formatted.");
	}

	&VerifyRecipeIngredientsFormat($ingredients);

	# Turn off auto-commit. This way if anything fails we can bail and
	# any changes we've made will be undone (so we don't get half a recipe).
	$dbh->{'AutoCommit'} = 0;
	if($dbh->{'AutoCommit'}) {
		&PrintErrorExit($ls_set_autocommit_off_failed{$language});
	}

	if($cmd eq "save_edited") {
		&UpdateRecipeBaseInfo($l_recipe_id, $name, $yield_qty, $yield_units, $source);
		&DeleteRecipeIngredients($l_recipe_id);
		&DeleteRecipeInstructions($l_recipe_id);
		&DeleteRecipeCategories($l_recipe_id);
	} elsif($cmd eq "save_new") {	# This check is probably unnecessary. Oh well.
		$l_recipe_id = &InsertRecipeBaseInfo($name, $yield_qty, $yield_units, $source, $user_id);
	}

	&InsertRecipeIngredientsFormatted($l_recipe_id, $ingredients);
	&InsertRecipeInstructionsFormatted($l_recipe_id, $instructions);

	# Categories are optional
	if($#categories >= 0) {
		&InsertRecipeCategories($l_recipe_id, @categories);
	}

	# If the program hasn't exited by now, everything worked.
	$dbh->commit();
	$dbh->{'AutoCommit'} = 1;

	# Do template for success message
	$output = &GetTemplate("recipe_add_success.html");

	$output =~ s/REP_RECIPE_NAME/$name/g;
	$output =~ s/REP_RECIPE_ID/$l_recipe_id/g;

	&PrintSuccessExit($output);
}


#####################################################################
# UpdateRecipeBaseInfo($recipe_id, $name, $yield_qty, $yield_units, $source)
#
# Updates base info for recipe recipe_id (RECIPES table)
#####################################################################
sub UpdateRecipeBaseInfo() {
	my($l_recipe_id, $name, $yield_qty, $yield_units, $source) = @_;
	my($now_utime);
	chomp($name, $yield_qty, $yield_units, $source);

	$now_utime = time();

	$sth = &ExecSQL(
		"UPDATE recipes " .
		"SET name='$name', yield_qty=$yield_qty, yield_units='$yield_units', " .
			"source='$source', mod_utime='$now_utime' " .
		"WHERE recipe_id=$l_recipe_id"
		);
}


#####################################################################
# InsertRecipeBaseInfo($name, $yield_qty, $yield_units, $source)
#
# Inserts base info for recipe recipe_id (RECIPES table).
# Returns the recipe_id of the new recipe.
#####################################################################
sub InsertRecipeBaseInfo() {
	my($name, $yield_qty, $yield_units, $source, $l_user_id) = @_;
	my($oid, $row, $new_recipe_id, $now_utime);
	chomp($name, $yield_qty, $yield_units, $source);

	$now_utime = time();

	# Getting new recipe_id is DB-dependant, so do the right thing for the DB
	if($db_driver eq "Oracle") {
		# Can't easily get the new ROWID from Oracle, so do it manually with
		# the sequence instead.
		$sth = &ExecSQL(
			"SELECT seq_recipes_recipe_id.NEXTVAL AS new_recipe_id " .
			"FROM dual"
			);

		# Make sure we got it
		if($row = $sth->fetchrow_hashref) {
			$new_recipe_id = $row->{'new_recipe_id'};
		}

		unless($new_recipe_id) {
			&PrintErrorExit("InsertRecipeBaseInfo(): " . $ls_cant_get_new_recipe_id{$language});
		}

		$sth = &ExecSQL(
			"INSERT INTO recipes (recipe_id, name, yield_qty, yield_units, source, " .
				"author_user_id, create_utime, mod_utime) " .
			"VALUES ($new_recipe_id, '$name', $yield_qty, '$yield_units', '$source', " .
				"$l_user_id, '$now_utime', '$now_utime')"
			);
	
	} elsif($db_driver eq "Pg" || $db_driver eq "mysql") {

		# Insert directly for Postgres & MySQL
		$sth = &ExecSQL(
			"INSERT INTO recipes (name, yield_qty, yield_units, source, " .
				"author_user_id, create_utime, mod_utime) " .
			"VALUES ('$name', $yield_qty, '$yield_units', '$source', " .
				"$l_user_id, '$now_utime', '$now_utime')"
			);

		# Get the newly created recipe_id which is generated by a 
		# sequence in the database. Database-dependant.
	
		# Postgres
		if($db_driver eq "Pg") {
			$oid = $sth->{pg_oid_status};
	
			$sth = &ExecSQL(
				"SELECT recipe_id " .
				"FROM recipes " .
				"WHERE oid=$oid"
				);
	
			if($row = $sth->fetchrow_hashref) {
				$new_recipe_id = $row->{'recipe_id'};
			}
		}
	
		# MySQL
		elsif($db_driver eq "mysql") {
			$new_recipe_id = $sth->{mysql_insertid};
		}
	
		# Did we get the new recipe id?
		if($new_recipe_id) {
			return($new_recipe_id);
		} else {
			&PrintErrorExit("InsertRecipeBaseInfo(): " . $ls_cant_get_new_recipe_id{$language});
		}
	}
}




#####################################################################
# VerifyRecipeIngredientsFormat($ingredients_formatted)
#
# Takes a lump of ingredients and verifies the format 
# ("name*qty*unit_abbr", one per line)
#####################################################################
sub VerifyRecipeIngredientsFormat() {
	my($ingredients_formatted) = @_;

	foreach $this_ingredient_line (split(/\n/, $ingredients_formatted)) {	# split lump into lines
		# Veryify format
		unless($this_ingredient_line =~ /\w+\*(\d+|\d*\.\d+|\d+\s\d+\/\d+|\d+\/\d+)\*\w+/) {
			&EditRecipeScreenError($ls_bad_ingredient_format{$language});
		}
	}
}



#####################################################################
# InsertRecipeIngredientsFormatted($recipe_id, $ingredients_formatted)
#
# Takes a lump of ingredients formatted "name*qty*unit_abbr", one per
# line and inserts them for recipe recipe_id.
#####################################################################
sub InsertRecipeIngredientsFormatted() {
	my($l_recipe_id, $ingredients_formatted) = @_;
	my($this_ingredient_line, $name, $qty, $unit_id, $ctr);

	# Fixed double-spaced lumps
	$ingredients_formatted =~ s/\r//g;		# Ditch \r's
	$ingredients_formatted =~ s/\n\n+/\n/g;	# Ditch extra \n's: >= 2 \n's to 1
	chomp($ingredients_formatted);

	$ctr = 1;
	$unit_id = -1;

	foreach $this_ingredient_line (split(/\n/, $ingredients_formatted)) {	# split lump into lines

		# Note: format has already been verified by VerifyRecipeIngredientsFormat()
		($name, $qty, $unit_abbr) = split(/\*/, $this_ingredient_line);
		chomp($name, $qty, $unit_abbr);

		# Convert mixed fraction to decimal
		$qty = frac($qty);
		$qty = eval($qty);

		# Convert unit abbreviation to unit_id; bail if not found
		# This might read from the DB at some point, it just seems wasteful to do so
		$unit_abbr = lc($unit_abbr);
		$unit_id   = $unit_map_abbr2id{$unit_abbr};

		if($unit_id < 1 || $unit_id > 15) {
			&EditRecipeScreenError(
				$ls_the_unit{$language} . " <B>$unit_abbr</B> " .
				$ls_doesnt_exist{$language} . "." . 
				$ls_check_ingredients_box{$language});
		}

		&InsertRecipeIngredient($l_recipe_id, $ingredient_types{'normal'},
			$ctr++, $name, $qty, $unit_id);

		$unit_id = -1;
	}
}


#####################################################################
# InsertRecipeIngredient($recipe_id, $ingredient_type, $display_order,
#						 $name, $qty, $unit_id)
#
# Adds an ingredient record for recipe recipe_id.
#####################################################################
sub InsertRecipeIngredient() {
	my($l_recipe_id, $ingredient_type, $display_order, $name, $qty, $unit_id, $sql) = @_;

	$sth = &ExecSQL(
		"INSERT INTO ingredients " .
		"(recipe_id, ingredient_type, display_order, name, qty, unit_id) " .
		"VALUES " .
		"($l_recipe_id, $ingredient_type, $display_order, '$name', $qty, $unit_id)"
	);
}


#####################################################################
# DeleteRecipeIngredients($recipe_id)
#
# Deletes all ingredient entries for an associated recipe_id.
#####################################################################
sub DeleteRecipeIngredients() {
	my($l_recipe_id) = @_;

	$sth = &ExecSQL(
		"DELETE FROM ingredients " .
		"WHERE recipe_id=$l_recipe_id"
		);
}


#####################################################################
# InsertRecipeInstructionsFormatted($recipe_id, $instructions_formatted)
#
# Adds instructions for recipe recipe_id. Pass it an array, one
# instruction per element, in order.
#####################################################################
sub InsertRecipeInstructionsFormatted() {
	my($l_recipe_id, $instructions_formatted) = @_;
	my($step_num);

	# Fixed double-spaced lumps as a courtesy
	$instructions_formatted =~ s/\r//g;		# Ditch \r's
	$instructions_formatted =~ s/\n+/\n/g;	# Multiple newlines to one
	chomp($instructions_formatted);

	$step_num = 1;
	foreach $instruction (split(/\n/, $instructions_formatted)) {
		&InsertRecipeInstruction($l_recipe_id, $step_num++, $instruction);
	}
}


#####################################################################
# InsertRecipeInstruction($recipe_id, $step_num, $step_text)
#
# Adds an instruction record for recipe recipe_id.
#####################################################################
sub InsertRecipeInstruction() {
	my($l_recipe_id, $step_num, $step_text) = @_;
	trim(chomp($step_text));

	# Make sure it'll fit in the db column
	if(length($step_text) > 4000) {
		&PrintErrorExit("InsertRecipeInstruction($l_recipe_id): " .
			$ls_instructions_for_step{$language} . $step_num .
			$ls_are_too_long{$language});
	}

	$sth = &ExecSQL(
		"INSERT INTO instructions (recipe_id, step_num, step_text) " .
		"VALUES ($l_recipe_id, $step_num, '$step_text')"
		);
}


#####################################################################
# DeleteRecipeInstructions($recipe_id)
#
# Deletes all instruction entries for an associated recipe_id.
#####################################################################
sub DeleteRecipeInstructions() {
	my($l_recipe_id) = @_;

	$sth = &ExecSQL(
		"DELETE FROM instructions " .
		"WHERE recipe_id=$l_recipe_id"
		);
}


#####################################################################
# DeleteRecipe($recipe_id)
#
# Deletes recipe recipe_id.
#####################################################################
sub DeleteRecipe() {
	my($l_recipe_id) = @_;

	# Verify access
	unless($logged_in && &UserHasPermission($user_id, $perm_delete_any_recipe)) {
		&PrintErrorExit($ls_no_delete_recipe_perm{$language});
	}

	&DeleteRecipeCategories($l_recipe_id);
	&DeleteRecipeIngredients($l_recipe_id);
	&DeleteRecipeInstructions($l_recipe_id);

	# Delete bookmark entries for recipe
	$sth = &ExecSQL(
		"DELETE FROM user_recipe_bookmarks " .
		"WHERE recipe_id=$l_recipe_id"
		);

	# Delete main recipe entry
	$sth = &ExecSQL(
		"DELETE FROM recipes " .
		"WHERE recipe_id=$l_recipe_id"
		);

	&PrintSuccessExit($ls_recipe_deleted{$language});
}


#####################################################################
# InsertRecipeCategories($recipe_id, @instructions)
#
# Adds categories for recipe recipe_id. Pass it an array, one
# recipe_id per element.
#####################################################################
sub InsertRecipeCategories() {
	my($l_category_id, @categories) = @_;
	my($category);

	foreach $category (@categories) {
		&InsertRecipeCategory($l_category_id, $category);
	}
}


#####################################################################
# InsertRecipeCategory($recipe_id, $category_id)
#
# Adds a category record for recipe $recipe_id in category
# $category_id.
#####################################################################
sub InsertRecipeCategory() {
	my($l_recipe_id, $category_id) = @_;

	$sth = &ExecSQL(
		"INSERT INTO category_entries (recipe_id, category_id) " .
		"VALUES ($l_recipe_id, $category_id)"
		);
}

# END recipe_editor.cgi
