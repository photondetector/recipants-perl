#!/usr/bin/perl

###########################################################################
# File      : recipe_search.cgi
# Purpose	: Searches for recipes
# Program   : ReciPants ( http://recipants.photondetector.com/ )
# Version   : 1.0
# Author    : Nick Grossman <nick@photondetector.com>
# Tab stops : 4
#
# Copyright (c) 2002, 2003
#     Nicolai Grossman <nick@photondetector.com>
#     Benjamin Mehlman <ben-recipe@cownow.com>
#     Marc Hartstein   <mahartstein@vassar.edu>
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

require "librecipants.pl";

# _____ GLOBAL VARIABLES ____________________________________________

$cmd        = lc(param('cmd'));
$search_for = trim(lc(param('search_for')));
$and_or_or;

# _____ END GLOBAL VARIABLES ________________________________________


&InitUser();


# If we don't have a command argument, assume we're searching
if(! $cmd) {
	# Make sure we have input
	unless($search_for) {
		&ShowAdvancedSearchScreen($ls_no_search_term{$language});
		&CleanExit(0);
	}

	# Set up search type (ANY/OR, ALL/AND). ANY/OR is the default.
	# We'll use this later when we build the WHERE clause for the DB query.
	if(lc(param('search_type')) eq "all") {
		$and_or_or = "AND";
	} else {
		$and_or_or = "OR";
	}

	# We have clearance, Clarenece!
	&KeywordSearch($search_for);

# Otherwise, show the advanced search screen
} else {
	&ShowAdvancedSearchScreen();
}


&CleanExit(0);


# _____ FUNCTIONS ___________________________________________________

#####################################################################
# KeywordSearch(@search_terms)
#
# Performs a keyword search for @search_terms in the appropriate
# places (recipe names, ingredients, and instruction text).
#####################################################################
sub KeywordSearch() {
	my($search_terms) = @_;
	my($output, @terms, $name_results, $ingredient_results, $instruction_results);

	$output = &GetTemplate("search_results.html");

	# Put each search term into a list
	##### INSERT REGEX to translate >= 2 spaces to one space #####
	@terms = split(" ", $search_terms);

	# Search each area selected for search and turn on the appropriate form checkboxes
	if(param('name')) {
		$name_results = &SearchNames(@terms);
		$output =~ s/<INPUT NAME=\"name\" TYPE=\"checkbox\">/<INPUT NAME=\"name\" TYPE=\"checkbox\" CHECKED>/g;
	} else {
		$name_results = "";
	}

	if(param('ingredients')) {
		$ingredient_results = &SearchIngredients(@terms);
		$output =~ s/<INPUT NAME=\"ingredients\" TYPE=\"checkbox\">/<INPUT NAME=\"ingredients\" TYPE=\"checkbox\" CHECKED>/g;
	} else {
		$ingredient_results = "";
	}

	if(param('instructions')) {
		$instruction_results = &SearchInstructions(@terms);
		$output =~ s/<INPUT NAME=\"instructions\" TYPE=\"checkbox\">/<INPUT NAME=\"instructions\" TYPE=\"checkbox\" CHECKED>/g;
	} else {
		$instruction_results = "";
	}

	# If no search area was selected, do a default search in recipe name
	if(! param('name') && ! param('ingredients') && ! param('instructions')) {	
		$name_results = &SearchNames(@terms);
		$output =~ s/<INPUT NAME=\"name\" TYPE=\"checkbox\">/<INPUT NAME=\"name\" TYPE=\"checkbox\" CHECKED>/g;
	}

	# Populate output template
	$output =~ s/REP_SEARCH_FOR/$search_for/g;
	$output =~ s/REP_NAME_RESULTS/$name_results/g;
	$output =~ s/REP_INGREDIENT_RESULTS/$ingredient_results/g;
	$output =~ s/REP_INSTRUCTION_RESULTS/$instruction_results/g;
	&ShowPage($ls_search_results_for{$language} . $search_for, $output);
}


#####################################################################
# SearchNames(@search_terms)
#
# Returns a chunk of HTML containing links to recipes that match
# @search_terms in recipe names.
#####################################################################
sub SearchNames() {
	my(@search_terms) = @_;
	my($total, $num_matches, $names, $names_output);
	$template = &GetTemplate("search_results_names.html");

	# Build WHERE clause
	for $term_number (0 .. $#search_terms) {
		if($term_number == 0) {		# If we're first, add open paren
			$where_clause = "(";
		}

		$where_clause .= "LOWER(name) LIKE '%$_[$term_number]%' ";

		if($term_number <= ($#search_terms - 1)) {	# If we're not last
			$where_clause .= "$and_or_or ";
		} else {									# We're last
			$where_clause .= ")";
		}
	}

	$sth = &ExecSQL(
		"SELECT recipe_id, name " .
		"FROM recipes " .
		"WHERE $where_clause " . 
		"ORDER BY name"
		);

	$num_matches = 0;

	while(my $row = $sth->fetchrow_hashref) {
		$names .= "<SPAN CLASS=\"recipe-link\"><A HREF=\"recipe.cgi?recipe_id=$row->{'recipe_id'}\">$row->{'name'}</A></SPAN><BR>\n";
		$num_matches++;
	}

	if($num_matches == 0) {
		$names = $ls_no_recipe_name_matches{$language};
	}

	# Populate output template
	$template =~ s/REP_NUM_HITS/$num_matches/g;
	$template =~ s/REP_RESULTS/$names/g;
	return($template);
}


#####################################################################
# SearchIngredients(@search_terms)
#
# Returns a chunk of HTML containing links to recipes that match
# @search_terms in ingredient names.
#####################################################################
sub SearchIngredients() {
	my(@search_terms) = @_;
	my($num_matches, $ingredients, $where_clause);

	$template = &GetTemplate("search_results_ingredients.html");

	# Build WHERE clause
	for $term_number (0 .. $#search_terms) {
		if($term_number == 0) {		# If we're first, add open paren
			$where_clause = "(";
		}

		$where_clause .= "LOWER(i.name) LIKE '%$_[$term_number]%' ";

		if($term_number <= ($#search_terms - 1)) {	# If we're not last
			$where_clause .= "$and_or_or ";
		} else {									# We're last
			$where_clause .= ")";
		}
	}

	$sth = &ExecSQL(
		"SELECT DISTINCT i.recipe_id, r.name " .
		"FROM ingredients i, recipes r " .
		"WHERE $where_clause AND r.recipe_id=i.recipe_id " .
		"ORDER BY r.name"
		);

	$num_matches = 0;

	while(my $row = $sth->fetchrow_hashref) {
		$ingredients .= "<SPAN CLASS=\"recipe-link\"><A HREF=\"recipe.cgi?recipe_id=$row->{'recipe_id'}\">$row->{'name'}</A></SPAN><BR>\n";
		$num_matches++;
	}

	if($num_matches == 0) {
		$ingredients = $ls_no_ingredient_matches{$language};
	}

	# Populate output template
	$template =~ s/REP_NUM_HITS/$num_matches/g;
	$template =~ s/REP_RESULTS/$ingredients/g;
	return($template);
}


#####################################################################
# SearchInstructions(@search_terms)
#
# Returns a chunk of HTML containing links to recipes that match
# @search_terms in instruction text.
#####################################################################
sub SearchInstructions() {
	my(@search_terms) = @_;
	my($num_matches, $instructions, $where_clause);

	$template = &GetTemplate("search_results_instructions.html");

	# Build WHERE clause
	for $term_number (0 .. $#search_terms) {
		if($term_number == 0) {		# If we're first, add open paren
			$where_clause = "(";
		}

		$where_clause .= "LOWER(instructions.step_text) LIKE '%$_[$term_number]%' ";

		if($term_number <= ($#search_terms - 1)) {	# If we're not last
			$where_clause .= "$and_or_or ";
		} else {									# We're last
			$where_clause .= ")";
		}
	}

	$sth = &ExecSQL(
		"SELECT DISTINCT instructions.recipe_id, recipes.name " .
		"FROM instructions, recipes " .
		"WHERE $where_clause AND recipes.recipe_id=instructions.recipe_id " .
		"ORDER BY recipes.name"
		);

	$num_matches = 0;

	while(my $row = $sth->fetchrow_hashref) {
		$names .= "<SPAN CLASS=\"recipe-link\"><A HREF=\"recipe.cgi?recipe_id=$row->{'recipe_id'}\">$row->{'name'}</A></SPAN><BR>\n";
		$num_matches++;
	}

	if($num_matches == 0) {
		$names = $ls_no_instruction_matches{$language};
	}

	# Populate output template
	$template =~ s/REP_NUM_HITS/$num_matches/g;
	$template =~ s/REP_RESULTS/$names/g;
	return($template);
}


#####################################################################
# ShowAdvancedSearchScreen($error_message)
#
# Gee willakers, I wonder what this does!
#####################################################################
sub ShowAdvancedSearchScreen() {
	my($error_message) = @_;
	my($output, $error_box);

	$output = &GetTemplate("search_box.html");

	# Handle error message if we got one
	if($error_message) {
		$error_box = &GetTemplate("error_box.html");
		$error_box =~ s/REP_MESSAGE/$error_message/g;
		$output = $error_box . $output;
	}

	&ShowPage($ls_advanced_search_title{$language}, $output);
}

# END recipe_search.cgi
