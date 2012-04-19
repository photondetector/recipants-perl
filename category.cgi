#!/usr/bin/perl

###########################################################################
# File      : category.cgi
# Purpose   : Handles viewing by category.
# Program   : ReciPants ( http://recipants.photondetector.com/ )
# Version   : 1.0.1
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

$category_id = param('category_id');


# _____ END GLOBAL VARIABLES ________________________________________


&InitUser();	# Set up user info

# Make sure we have input
if(! param('category_id') && param('category_id') != 0) {
	&PrintErrorExit($ls_no_category_id{$language});
}

if(param('cmd') eq "tree") {
	&ShowCategoryTree();
} else {
	&ShowCategory(param('category_id'));
}
            
&CleanExit(0);


# _____ FUNCTIONS ___________________________________________________

#####################################################################
# ShowCategory($category_id)
#
# Shows Current category w/ breadcrumb trail, subcategories, and
# links to recipes in $category_id.
#####################################################################
sub ShowCategory() {
	my($l_category_id) = @_;
	my($breadcrumb_trail, $subcategories, %recipes, $recipe_name, $recipe_id,
		$category_output, $subcategory_output, $recipe_output);

	# Do breadcrumb trail for the category we're in
	$breadcrumb_trail = &GetCategoryBreadcrumbsHTML($l_category_id, 0, 1);
	$category_output  = &GetTemplate("category_category.html");
	$category_output  =~ s/REP_BREADCRUMBS/$breadcrumb_trail/g;

	# Do subcategories
	$subcategories = &GetSubcategoriesHTML($l_category_id);
	if($subcategories eq "") {	# Set not found message if we didn't get anything
		$subcategories = $ls_no_subcategories_in_category{$language};
	}

	$subcategory_output = &GetTemplate("category_subcategories.html");
	$subcategory_output =~ s/REP_SUBCATEGORIES/$subcategories/g;


	# Do recipes in this category
	%recipes_here = &GetRecipesInCategory($l_category_id);

	# If we have got recipes build display buffer, otherwise set not found message
	if(scalar(keys(%recipes_here)) != 0) {
		foreach $recipe_id (keys %recipes_here) {
			$recipe_name = $recipes_here{$recipe_id};
			$recipes    .= "<A HREF=\"recipe.cgi?recipe_id=$recipe_id\">" .
				"$recipe_name</A><BR>\n";
		}
	} else {	# Set not found message
		$recipes = $ls_no_recipes_in_category{$language};
	}

	$recipe_output = &GetTemplate("category_recipes.html");
	$recipe_output =~ s/REP_RECIPES/$recipes/g;

	&ShowPage($ls_categories_title{$language},
		$category_output . $subcategory_output . $recipe_output);
}


#####################################################################
# ShowCategoryTree()
#
# Shows the whole category tree.
#####################################################################
sub ShowCategoryTree() {
	my($output, $category_tree);

	$category_tree = &GetCategoryTreeLinks();

	$output = &GetTemplate("category_tree.html");
	$output =~ s/REP_CATEGORY_TREE/$category_tree/g;

	&ShowPage($ls_category_tree_title{$language}, $output);
}

# END category.cgi
