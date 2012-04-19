#!/usr/bin/perl

###########################################################################
# File      : recipe.cgi
# Purpose   : Handles display, scaling, and format conversion of recipes.
# Program   : ReciPants ( http://recipants.photondetector.com/ )
# Version   : 1.1.1
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

$recipe_id = param('recipe_id');

# _____ END GLOBAL VARIABLES ________________________________________


&InitUser();	# Set up user info


# We need a recipe ID for everything except adding a new recipe
unless($recipe_id) {
	&PrintErrorExit($ls_no_recipe_id{$language});
}

# Figure out our output format and do it. HTML is default.
if(param('format') eq "xml") {		# XML uses the RecipeML DTD
	&RenderRecipeXML($recipe_id, param('scale_factor'));
} elsif(param('format') eq "mealmaster") {
	&RenderRecipeMealMaster($recipe_id, param('scale_factor'));
} elsif(param('format') eq "html_printer") {
	&RenderRecipeHTMLPrinterFriendly($recipe_id, param('scale_factor'));
} elsif(param('cmd') eq "email") {
	&EmailRecipe($recipe_id);
} else {
	&RenderRecipeHTML($recipe_id, param('scale_factor'));
}

&CleanExit(0);


# _____ FUNCTIONS  __________________________________________________

#####################################################################
# RenderRecipeHTML($recipe_id, $scale_factor)
#
# Displays recipe $recipe_id, optionally scaled to $scale_factor
# in HTML.
#####################################################################
sub RenderRecipeHTML() {
	my($l_recipe_id, $display_scale_factor) = @_;
	my(%base_info, $source, @ingredients, @instructions, $ingredient_template,
		$this_ingredient, $ingredients_output, $instructions_output, 
		$recipe_name, @categories, $categories_ouput, $ctr,
		$recipe_admin_menu, $recipe_admin_menu_options, $num_admin_options,
		$decimal_scale_factor, $email_recipe_form);

	$output  = &GetTemplate("recipe.html");

	# Convert mixed fraction to decimal
	if($display_scale_factor && $display_scale_factor ne "1" &&
		$display_scale_factor ne "0")
	{
		$decimal_scale_factor = eval(frac(&trim($display_scale_factor)));
	}

	$base_info    = &GetRecipeBaseInfo($l_recipe_id);
	@ingredients  = &GetRecipeIngredients($l_recipe_id, $decimal_scale_factor);
	@instructions = &GetRecipeInstructions($l_recipe_id);
	@categories   = &GetCategoryBreadcrumbsForRecipeHTML($l_recipe_id, 1, 0); # link the last crumb and don't show the top category

	# Ingredients
	$ingredient_template = &GetTemplate("ingredient.html");

	for $i (0 .. $#ingredients) {
		$this_ingredient = $ingredient_template;
		$this_ingredient =~ s/REP_NAME/$ingredients[$i]->{'name'}/g;
		$this_ingredient =~ s/REP_UNIT/$ingredients[$i]->{'abbreviation'}/g;
		$this_ingredient =~ s/REP_QTY/$ingredients[$i]->{'qty'}/g;

		# Alternate background colors
		if($i % 2 == 0) {
			$this_ingredient =~ s/REP_BGCOLOR/CCCCCC/g;
		} else {
			$this_ingredient =~ s/REP_BGCOLOR/AAAAAA/g;
		}

		$ingredients_output .= $this_ingredient;
	}

	# Instructions
	$ctr = 1;
	foreach(@instructions) {
		$instructions_output .= "<BR><BR>" unless($ctr == 1);
		$instructions_output .= "<B>$ctr)</B> $_\n";
		$ctr++;
	}

	# Categories
	foreach(@categories) {
		$categories_output .= "$_<BR>";
	}

	# Selected base info
	if($decimal_scale_factor && $decimal_scale_factor != 1 && $decimal_scale_factor > 0) {
		$yield_qty = $base_info->{'yield_qty'} * $decimal_scale_factor;
		$recipe_name .= $base_info->{'name'} . " (" . 
			$ls_word_scaled{$language} . " x $display_scale_factor)";
	} else {
		$yield_qty = $base_info->{'yield_qty'};
		$recipe_name = $base_info->{'name'};
	}

	if($base_info->{'source'} ne "") {
		$source = $base_info->{'source'};
	} else {
		$source = $ls_word_unknown{$language};
	}

	# Recipe admin options:
	# If the user is logged in, get user's permissions and display 
	# links to administrative recipe actions that they can perform.
	#
	# Also display Favorite Recipes and Email Recipe To A Friend 
	# forms if they're logged in.
	if($logged_in) {
		# Do Email Recipe form regardless of permissions
		$email_recipe_form = &GetTemplate("recipe_email_form.html");

		# Do recipe bookmarks
		if(&UserHasRecipeBookmarked($user_id, $l_recipe_id)) {
			$recipe_bookmark_form = &GetTemplate("recipe_bookmark_form_bookmarked.html");
		} else {
			$recipe_bookmark_form = &GetTemplate("recipe_bookmark_form_not_bookmarked.html");
		}

		# Do Admin Menu
		$num_admin_options = 0;

		# Edit recipe? explicit grant or if owner matches
		if(&UserHasPermission($user_id, $perm_edit_any_recipe)) {
			$recipe_admin_menu_options .=
				"<A HREF=\"recipe_editor.cgi?cmd=edit&" .
				"recipe_id=$l_recipe_id\">" . $ls_edit_this_recipe{$language} .
				"</A>";

			$num_admin_options++;

		} elsif($base_info->{'author_user_id'} == $user_id) {

			$recipe_admin_menu_options .=
				"<A HREF=\"recipe_editor.cgi?cmd=edit&" .
				"recipe_id=$l_recipe_id\">" . $ls_edit_this_recipe{$language} .
				"</A>";

			$num_admin_options++;
		}

		# Delete recipe?
		if(&UserHasPermission($user_id, $perm_delete_any_recipe)) {
			# Line break if there are preceeding options
			if($num_admin_options > 0) {
				$recipe_admin_menu_options .= "<BR>\n";
			}

			$recipe_admin_menu_options .=
				"<A HREF=\"recipe_editor.cgi?cmd=delete&" .
				"recipe_id=$l_recipe_id\" " .
				"onClick=\"javascript:return confirm('" . 
				$ls_delete_recipe_confirm_js{$language} . "');\">" .
				$ls_delete_this_recipe{$language} . "</A>";

			$num_admin_options++;
		}

		# If we have any admin options, get the admin menu template
		if($num_admin_options > 0) {
			$recipe_admin_menu = &GetTemplate("recipe_admin_menu.html");
		}

		$recipe_admin_menu =~ s/REP_MENU_OPTIONS/$recipe_admin_menu_options/g;
	}

	# Populate and print the output template
	$output =~ s/REP_RECIPE_ADMIN_MENU/$recipe_admin_menu/g;
	$output =~ s/REP_EMAIL_RECIPE_FORM/$email_recipe_form/g;
	$output =~ s/REP_RECIPE_BOOKMARK_FORM/$recipe_bookmark_form/g;
	$output =~ s/REP_RECIPE_ID/$l_recipe_id/g;
	$output =~ s/REP_CATEGORIES/$categories_output/g;
	$output =~ s/REP_INGREDIENTS/$ingredients_output/g;
	$output =~ s/REP_INSTRUCTIONS/$instructions_output/g;
	$output =~ s/REP_YIELD_QTY/$yield_qty/g;
	$output =~ s/REP_YIELD_UNITS/$base_info->{'yield_units'}/g;
	$output =~ s/REP_SOURCE/$source/g;
	$output =~ s/REP_SUBMITTER_NAME/$base_info->{'user_name'}/g;
	$output =~ s/REP_SUBMITTER_USER_ID/$base_info->{'author_user_id'}/g;
	$output =~ s/REP_SCALE_FACTOR/$decimal_scale_factor/g;
	&ShowPage($ls_word_recipe{$language} . ": $recipe_name", $output);
}


#####################################################################
# RenderRecipeHTMLPrinterFriendly($recipe_id, $scale_factor)
#
# Displays recipe $recipe_id, optionally scaled to $scale_factor
# in printer-friendly HTML.
#####################################################################
sub RenderRecipeHTMLPrinterFriendly() {
	my($l_recipe_id, $display_scale_factor) = @_;
	my(%base_info, $source, @ingredients, @instructions, $ingredient_template,
		$this_ingredient, $ingredients_output, $instructions_output, 
		$recipe_name, $ctr, $decimal_scale_factor);

	$base_info = &GetRecipeBaseInfo($l_recipe_id);

	# Do file name - do the export file business rather than print it
	# directly to the browser so they get a meaningful file name rather
	# than the name of the CGI.
	$file_name = &EscapeFileName($base_info->{'name'} . ".html");

	# Optimization possible: stat attempted output file and template file,
	# and compare mod times against recipe mod time. Only fetch recipe from
	# DB and write file if file doesn't exist or is older than template or 
	# recipe mod time.
	open(HTML_PRINTER_OUT, "> $export_directory_html_printer$path_separator$file_name") || 
		&PrintErrorExit($ls_cant_open_export_file{$language} . $file_name . ": $!");

	$output = &GetTemplate("recipe_printer_friendly.html");

	# Convert mixed fraction to decimal
	if($display_scale_factor && $display_scale_factor ne "1" &&
		$display_scale_factor ne "0")
	{
		$decimal_scale_factor = eval(frac(&trim($display_scale_factor)));
	}

	@ingredients  = &GetRecipeIngredients($l_recipe_id, $decimal_scale_factor);
	@instructions = &GetRecipeInstructions($l_recipe_id);

	# Ingredients
	$ingredient_template = &GetTemplate("ingredient_printer_friendly.html");
	for $i (0 .. $#ingredients) {
		$this_ingredient = $ingredient_template;
		$this_ingredient =~ s/REP_NAME/$ingredients[$i]->{'name'}/g;
		$this_ingredient =~ s/REP_UNIT/$ingredients[$i]->{'abbreviation'}/g;
		$this_ingredient =~ s/REP_QTY/$ingredients[$i]->{'qty'}/g;

		$ingredients_output .= $this_ingredient;
	}

	# Instructions
	$ctr = 1;
	foreach(@instructions) {
		$instructions_output .= "<P><B>$ctr)</B> $_\n";
		$ctr++;
	}

	# Selected base info
	if($decimal_scale_factor && $decimal_scale_factor != 1 && $decimal_scale_factor > 0) {
		$yield_qty = $base_info->{'yield_qty'} * $decimal_scale_factor;
		$recipe_name .= $base_info->{'name'} . " (" . 
			$ls_word_scaled{$language} . " x $display_scale_factor)";
	} else {
		$yield_qty = $base_info->{'yield_qty'};
		$recipe_name = $base_info->{'name'};
	}

	if($base_info->{'source'} ne "") {
		$source = $base_info->{'source'};
	} else {
		$source = $ls_word_unknown{$language};
	}

	# Populate and print the output template
	$output =~ s/REP_RECIPE_NAME/$recipe_name/g;
	$output =~ s/REP_INGREDIENTS/$ingredients_output/g;
	$output =~ s/REP_INSTRUCTIONS/$instructions_output/g;
	$output =~ s/REP_YIELD_QTY/$yield_qty/g;
	$output =~ s/REP_YIELD_UNITS/$base_info->{'yield_units'}/g;
	$output =~ s/REP_SOURCE/$source/g;
	$output =~ s/REP_SUBMITTER_NAME/$base_info->{'user_name'}/g;
	$output =~ s/REP_APP_NAME/$app_name/g;
	$output =~ s/REP_APP_VERSION/$app_version/g;
	$output =~ s/REP_APP_HOST_TITLE/$app_host_title/g;
	$output =~ s/REP_APP_HOST_URL/$app_host_url/g;
	$output =~ s/REP_APP_INSTALLED_URL/$app_installed_url/g;
	
	print HTML_PRINTER_OUT $output;
	close(HTML_PRINTER_OUT);

	# Redirect to export file
	print header(-Location => "$export_directory_html_printer$path_separator$file_name");
}


#####################################################################
# RenderRecipeXML($recipe_id, $scale_factor)
#
# NOTE: Writes output to a file and issues an HTTP redirect to it
# so that the browser gets a meaningful file name.
#
# Displays recipe $recipe_id, optionally scaled to $scale_factor
# in XML using the RecipeML DTD. More info on RecipeML at
# http://www.formatdata.com/recipeml/
# -------------------------------------------------------------------
# As required:
# RecipeML Public License Version 1.0
#
# Copyright (c) FormatData. All rights reserved.
#
# Definitions
#
# "RecipeML Data" refers to a unit of data with RecipeML markup that is
# meant to comply with the RecipeML specification as posted on the
# FormatData site.
#
# "RecipeML Processing Software" refers to software written by a third
# party that reads, creates, edits, stores or otherwise processes RecipeML
# data according to the rules set forth in the RecipeML specification and
# DTD ("RecipeML format"). Generic XML processors are exempt from this
# definition.
#
# Requirements
#
# Distribution of RecipeML Processing Software in source and/or binary
# forms is permitted provided that the following conditions are met:
#
#   1. Distributions in source code must retain the above copyright
#      notice and this list of conditions.
#   2. Distributions in binary form must reproduce the above copyright
#      notice and this list of conditions in the documentation and/or other
#      materials provided with the distribution.
#   3. All advertising materials and documentation for RecipeML
#      Processing Software must display the following acknowledgment:
#      "This product is RecipeML compatible."
#   4. Names associated with RecipeML or FormatData must not be used to
#      endorse or promote RecipeML Processing Software without prior written
#      permission from FormatData. For written permission, please contact
#      RecipeML@formatdata.com.
#####################################################################
sub RenderRecipeXML() {
	my($l_recipe_id, $scale_factor) = @_;
	my( @ingredients,  $ingredient_template,  $this_ingredient,  $ingredients_output, 
		@instructions, $instruction_template, $this_instruction, $instructions_output,
		%base_info, $recipe_name, $source, $ctr, $file_name);

	# Get base info first for recipe (and therefore file) name
	$base_info = &GetRecipeBaseInfo($l_recipe_id);

	# Do file name - do the export file business rather than print it
	# directly to the browser so they get a meaningful file name rather
	# than the name of the CGI.
	$file_name = &EscapeFileName($base_info->{'name'} . ".xml");

	open(RECIPEML_OUT, "> $export_directory_recipeml$path_separator$file_name") || 
		&PrintErrorExit($ls_cant_open_export_file{$language} . $file_name . ": $!");

	$output  = &GetTemplate("recipe.xml");

	# We've successfully opened the export file, now do the rest...
	@ingredients  = &GetRecipeIngredients($l_recipe_id, $scale_factor);
	@instructions = &GetRecipeInstructions($l_recipe_id);

	# Instructions
	$instruction_template = &GetTemplate("instruction.xml");
	$ctr = 0;
	foreach(@instructions) {
		$this_instruction     = $instruction_template;
		$this_instruction     =~ s/REP_STEP_TEXT/$instructions[$ctr]/g;
		$instructions_output .= $this_instruction;
		$ctr++;
	}

	# Ingredients
	$ingredient_template = &GetTemplate("ingredient.xml");
	for $i (0 .. $#ingredients) {
		$this_ingredient = $ingredient_template;
		$this_ingredient =~ s/REP_NAME/$ingredients[$i]->{'name'}/g;
		$this_ingredient =~ s/REP_UNIT/$ingredients[$i]->{'abbreviation'}/g;
		$this_ingredient =~ s/REP_QTY/$ingredients[$i]->{'qty'}/g;
		$ingredients_output .= $this_ingredient;
	}

	# scale if necessary
	if($scale_factor && $scale_factor != 1) {
		$yield_qty = $base_info->{'yield_qty'} * $scale_factor;
		$recipe_name = $base_info->{'name'} . " (" . $ls_word_scaled{$language} .
			" x $scale_factor)";
	} else {
		$yield_qty = $base_info->{'yield_qty'};
		$recipe_name = $base_info->{'name'};
	}

	if($base_info->{'source'} ne "") {
		$source = $base_info{'source'};
	} else {
		$source = "Unknown";
	}

	# Populate and print the output template
	$output =~ s/REP_APP_NAME/$app_name/g;
	$output =~ s/REP_APP_VERSION/$app_version/g;
	$output =~ s/REP_INSTALLED_URL/$app_installed_url/g;
	$output =~ s/REP_NAME/$recipe_name/g;
	$output =~ s/REP_INGREDIENTS/$ingredients_output/g;
	$output =~ s/REP_INSTRUCTIONS/$instructions_output/g;
	$output =~ s/REP_YIELD_QTY/$yield_qty/g;
	$output =~ s/REP_YIELD_UNITS/$base_info->{'yield_units'}/g;
	$output =~ s/REP_SOURCE/$source/g;

	print RECIPEML_OUT $output;
	close(RECIPEML_OUT);

	# Redirect to export file
	print header(-Location => "$export_directory_recipeml$path_separator$file_name");
}


#####################################################################
# RenderRecipeMealMaster($recipe_id, $scale_factor)
#
# NOTES: 
# 1) Writes output to a file and issues an HTTP redirect to it
#    so that the browser gets a meaningful file name.
# 2) Static strings (except the word "Scaled") aren't localized
#    because they're part of the MM file format.
#
# Displays recipe $recipe_id, optionally scaled to $scale_factor
# in Meal-Master format.
#
# For more information about Meal-Master, go to its home page at
# http://home1.gte.net/welliver File format documentation is in the
# file "IMPORTF.DOC" (not an MS Word file) in the distribution.
#####################################################################
sub RenderRecipeMealMaster() {
	my($l_recipe_id, $scale_factor) = @_;
	my(%base_info, %category_info, $source, @ingredients, @instructions,
		$recipe_name, @categories, $category_name, $ctr, $file_name);

	# Since MM is a DOS app and only does 8.3 file names, use recipe ID
	# for the file name
	$file_name = "RP$l_recipe_id.TXT";

	open(MEALMASTER_OUT, "> $export_directory_mealmaster$path_separator$file_name") || 
		&PrintErrorExit($ls_cant_open_export_file{$language} . $file_name . ": $!");

	# Use \r\n for line breaks as Meal-Master is a DOS app
	$output  = "----- For Meal-Master v7.0+ - generated by $app_name v$app_version at $app_host_title\r\n";

	$base_info = &GetRecipeBaseInfo($l_recipe_id);
	@categories   = &GetCategoriesForRecipe($l_recipe_id);
	@ingredients  = &GetRecipeIngredients($l_recipe_id, $scale_factor);
	@instructions = &GetRecipeInstructions($l_recipe_id);

	# Handle scaling
	# Note there is no provision for a source attribution
	if($scale_factor && $scale_factor != 1 && $scale_factor > 0) {
		$yield_qty    = $base_info->{'yield_qty'} * $scale_factor;
		$recipe_name .= $base_info->{'name'} . " (" . $ls_word_scaled{$language} .
			" x $scale_factor)";
	} else {
		$yield_qty   = $base_info->{'yield_qty'};
		$recipe_name = $base_info->{'name'};
	}

	$output .= "      Title: $recipe_name\r\n";

	# Categories
	$output .= " Categories: ";

	if($#categories >= 0) {
		$ctr = 0;

		# Meal-Master allows a maximum of 5 categories
		if($#categories <= 4) {
			$last = $#categories;
		} else {
			$last = 4;
		}

		while($ctr <= $last) {
			%category_info = {};
			$category_info = &GetCategoryInfo($categories[$ctr]);

			# MM spec states that category names must have the first letter
			# capitalized and all else be lower case.
			$category_name = ucfirst(lc($category_info->{'name'}));

			# Handle commas
			if($ctr < $last) {	   # Not last
				$output .= $category_name;

				if($ctr <= ($last - 1)) {
					$output .= ",";
				}

				$output .= " ";
			} else {				# The only field
				$output .= $category_name;
			}

			$ctr++;
		}
	}
	$output .= "\r\n";

	# Yield
	$output .= "      Yield: $yield_qty " . $base_info->{'yield_units'} .
		"\r\n\r\n";

	# Ingredients
	for $i (0 .. $#ingredients) {
		if(length($ingredients[$i]->{'qty'}) >= 7) {
			&PrintErrorExit($ls_mm_qty_field_too_long{$language});
		}
	
		# Right-pad with spaces
		for(0 .. 6 - length($ingredients[$i]->{'qty'})) {
			$output .= " ";
		}
		$output .= $ingredients[$i]->{'qty'};
		$output .= " ";
		$output .= $unit_map_id2meal_master{$ingredients[$i]->{'unit_id'}};
		$output .= " ";
		$output .= $ingredients[$i]->{'name'};
		$output .= "\r\n";
	}
	$output .= "\r\n";

	# Instructions
	$ctr = 1;
	foreach(@instructions) {
		$output .= "$ctr) $_\r\n";
		$ctr++;
	}
	$output .= "\r\n";

	# End of recipe marker
	$output .= "-----\r\n";

	# We're done, write to file
	print MEALMASTER_OUT $output;
	close(MEALMASTER_OUT);

	# Redirect to export file
	print header(-Location => "$export_directory_mealmaster$path_separator$file_name");
}


#####################################################################
# RenderRecipeASCII($recipe_id, $scale_factor)
#
# Displays recipe $recipe_id, optionally scaled to $scale_factor
# in plain ASCII text.
#####################################################################
sub RenderRecipeASCII() {
	my($l_recipe_id, $scale_factor) = @_;
	my(%base_info, %category_info, $source, @ingredients, @instructions,
		$recipe_name, @categories, $category_name, $ctr, $file_name);

	$base_info = &GetRecipeBaseInfo($l_recipe_id);
	$file_name = &EscapeFileName($base_info->{'name'} . ".txt");

	open(MEALMASTER_OUT, "> $export_directory_plain_text$path_separator$file_name") || 
		&PrintErrorExit($ls_cant_open_export_file{$language} . $file_name . ": $!");

	$output = &GetFile("recipe.txt");

	@ingredients  = &GetRecipeIngredients($l_recipe_id, $scale_factor);
	@instructions = &GetRecipeInstructions($l_recipe_id);

	# Handle scaling
	if($scale_factor && $scale_factor != 1 && $scale_factor > 0) {
		$yield_qty    = $base_info->{'yield_qty'} * $scale_factor;
		$recipe_name .= $base_info->{'name'} . "\n(" . $ls_word_scaled{$language} .
			" x $scale_factor)";
	} else {
		$yield_qty   = $base_info->{'yield_qty'};
		$recipe_name = $base_info->{'name'};
	}

	# Yield
	$output .= "      Yield: $yield_qty " . $base_info->{'yield_units'} .
		"\r\n\r\n";

	# Ingredients
	for $i (0 .. $#ingredients) {
		if(length($ingredients[$i]->{'qty'}) >= 7) {
			&PrintErrorExit($ls_mm_qty_field_too_long{$language});
		}
	
		# Right-pad with spaces
		for(0 .. 6 - length($ingredients[$i]->{'qty'})) {
			$output .= " ";
		}
		$output .= $ingredients[$i]->{'qty'};
		$output .= " ";
		$output .= $ingredients[$i]->{'unit_id'};
		$output .= " ";
		$output .= $ingredients[$i]->{'name'};
		$output .= "\r\n";
	}

	# Instructions
	$ctr = 1;
	foreach(@instructions) {
		$output .= "$ctr) $_\r\n";
		$ctr++;
	}

	# We're done, write to file
	print MEALMASTER_OUT $output;
	close(MEALMASTER_OUT);

	# Redirect to export file
	print header(-Location => "$export_directory_mealmaster$path_separator$file_name");
}


#####################################################################
# EmailRecipe($recipe_id)
#
# Emails a link to recipe $recipe_id to
#####################################################################
sub EmailRecipe() {
	my($l_recipe_id) = @_;
	my($to_email, $from_email, $message, $recipe_base_info);

	# Bail if the user isn't logged in
	unless($logged_in) {
		&PrintErrorExit($ls_must_be_signed_in{$language});
	}

	$to_email = &trim(param('to_email'));

	# Check for required arg
	if($to_email eq "") {
		&PrintErrorExit($ls_missing_emai{$language});
		&CleanExit(0);
	}

	# Validate email address format
	unless(&EmailOK($to_email)) {
		&PrintErrorExit($ls_bad_email_format{$language});
		&CleanExit(0);
	}

	$from_email = &GetUserEmail($user_id);

	$message = &trim(param('message'));	# Firld not required
	unless($message) {
		$message = $ls_no_message{$language};
	}

	$recipe_base_info = &GetRecipeBaseInfo($l_recipe_id);

	# Fill out and send reminder email with account info
	$email_output = &GetTemplate("email_recipe_email.txt");
	$email_output =~ s/REP_INSTALLED_URL/$app_installed_url/g;
	$email_output =~ s/REP_APP_HOST_TITLE/$app_host_title/g;
	$email_output =~ s/REP_APP_HOST_URL/$app_host_url/g;
	$email_output =~ s/REP_APP_VERSION/$app_version/g;
	$email_output =~ s/REP_APP_URL/$app_url/g;
	$email_output =~ s/REP_FROM_EMAIL/$from_email/g;
	$email_output =~ s/REP_RECIPE_ID/$l_recipe_id/g;
	$email_output =~ s/REP_RECIPE_NAME/$recipe_base_info->{'name'}/g;
	$email_output =~ s/REP_MESSAGE/$message/g;

	&SendEmail($from_email, $from_email, $to_email, $to_email,
		$ls_email_recipe_subject{$language} . $recipe_base_info->{'name'},
		$email_output);

	&PrintSuccessExit($ls_email_recipe_success{$language} . $to_email);
}


#####################################################################
# GetUserEmail($user_id)
#
# Returns the email address for user $user_id.
#####################################################################
sub GetUserEmail() {
	my($l_user_id) = @_;
	my($row);

	$sth = &ExecSQL(
		"SELECT email " .
		"FROM users " .
		"WHERE user_id=$l_user_id"
		);

	if($row = $sth->fetchrow_hashref) {
		return($row->{'email'});
	} else {
		return("");
	}
}

# END recipe.cgi
