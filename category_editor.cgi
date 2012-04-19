#!/usr/bin/perl

###########################################################################
# File      : category_editor.cgi
# Purpose   : Category editing routines.
# Program   : ReciPants ( http://recipants.photondetector.com/ )
# Version   : 1.1
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

require "librecipants.pl";

# _____ GLOBAL VARIABLES ____________________________________________

$cmd         = param('cmd');
$category_id = param('category_id');
$parent      = param('parent');
$name        = trim(param('name'));

# _____ END GLOBAL VARIABLES ________________________________________


&InitUser();


# Verify access before we do anything else
unless($logged_in && &UserHasPermission($user_id, $perm_edit_any_category)) {
	&PrintErrorExit($ls_no_perm_edit_categories{$language});
}

# Do some quick arg checks
if(	($cmd eq "rename"   || $cmd eq "delete") && 
	($category_id eq "" || $category_id < 0))
{
	&PrintErrorExit($ls_no_category_id{$language});
}

if(($cmd eq "move" || $cmd eq "save_new") && ($parent eq "" || $parent < 0)) {
	&PrintErrorExit($ls_no_parent_category_id{$language});
}

# Check for name
if($name eq "" && ($cmd eq "save_new" || $cmd eq "rename")) {
	&CategoryEditorScreen($ls_missed_name_field{$language}, $error);
	&CleanExit(0);
}


# Do The Right Thing
if($cmd eq "save_new") {
	&InsertCategory($parent, $name);
	&CategoryEditorScreen($ls_category_added{$language}, $success);
}
elsif($cmd eq "rename") {
	&UpdateCategoryName($category_id, $name);
	&CategoryEditorScreen($ls_category_renamed{$language}, $success);
}
elsif($cmd eq "move") {
	&UpdateCategoryParent($category_id, $parent);
	&CategoryEditorScreen($ls_category_moved{$language}, $success);
}
elsif($cmd eq "delete") {
	&DeleteAllRecipesFromCategory($category_id);
	&DeleteCategory($category_id);
	&CategoryEditorScreen($ls_category_deleted{$language}, $success);
}
else {		# Default action
	&CategoryEditorScreen();
}


# We're done, clean up and go home
&CleanExit(0);


# _____ FUNCTIONS ___________________________________________________

#####################################################################
# CategoryEditorScreen($message, $message_type)
#
# Displays the category editor screen with an optional message.
# $message_type should be $error or $success.
#####################################################################
sub CategoryEditorScreen() {
	my($message, $message_type) = @_;
	my($output, $tree_template, $tree);

	$output = &GetTemplate("category_edit.html");

	# Get message template and fill it out
	if($message_type == $error) {
		$message_box = &GetTemplate("error_box.html");
	} elsif($message_type == $success) {
		$message_box = &GetTemplate("success_box.html");
	}
		
	$message_box =~ s/REP_MESSAGE/$message/g;
	$output =~ s/REP_MESSAGE/$message_box/g;

	# Category tree select lists
	# First get entire tree including master root category
	$tree_template = &GetCategoryTreeSelectList(-1);
	$tree = $tree_template;
	$tree =~ s/REP_ELEMENT_NAME/parent/g;
	$output =~ s/REP_TREE_PARENT/$tree/g;

	$tree = $tree_template;
	$tree =~ s/REP_ELEMENT_NAME/parent/g;
	$output =~ s/REP_TREE_PARENT/$tree/g;

	# Get tree w/o master root category
	$tree_template = &GetCategoryTreeSelectList(0);
	$tree = $tree_template;
	$tree =~ s/REP_ELEMENT_NAME/category_id/g;
	$output =~ s/REP_TREE_NO_TOP_CATEGORY_ID/$tree/g;

	&ShowPage($ls_category_editor_title{$language}, $output);
}


#####################################################################
# InsertCategory($parent, $name)
#
# Inserts a category category into the CATEGORIES table.
#####################################################################
sub InsertCategory() {
	my($parent, $name) = @_;
	my($oid, $row, $new_category_id);
	$name = &DBEscapeString(&trim($name));

	$sth = &ExecSQL(
		"INSERT INTO categories (parent, name) " .
		"VALUES ($parent, \'$name\')"
		);
}


#####################################################################
# UpdateCategoryParent($category_id, $parent)
#
# Updates parent for category category_id (CATEGORIES table)
#####################################################################
sub UpdateCategoryParent() {
	my($l_category_id, $l_parent) = @_;

	# Make sure we aren't moving a category under one of its children
	# as that branch would become orphaned.
	@trail = &GetCategoryBreadcrumbs($l_parent, 0);

	for $crumb_number (0 .. $#trail) {
		if($trail[$crumb_number]->{'category_id'} == $l_category_id) {
			&CategoryEditorScreen($ls_cant_move_category_under_child{$language}, $error);
			&CleanExit();
		}
	}

	$sth = &ExecSQL(
		"UPDATE categories " .
		"SET parent=$l_parent " .
		"WHERE category_id=$l_category_id"
		);
}


#####################################################################
# UpdateCategoryName($category_id, $name)
#
# Updates the name for category category_id (CATEGORIES table)
#####################################################################
sub UpdateCategoryName() {
	my($l_category_id, $l_name) = @_;

	$name = &DBEscapeString(trim($name));

	$sth = &ExecSQL(
		"UPDATE categories " .
		"SET name='$l_name' " .
		"WHERE category_id=$l_category_id"
		);
}


#####################################################################
# DeleteCategory($category_id)
#
# Deletes category category_id.
#####################################################################
sub DeleteCategory() {
	my($l_category_id) = @_;
	my($branch, $this_category);

	if($l_category_id == 0) {
		&CategoryEditorScreen($ls_cant_delete_root_category{$language}, $error);
	}

	# Get our branches of the category tree.
	$this_category = &GetCategoryInfo($l_category_id);

	@tree = ();
	&GetCategoryTree($l_category_id, 0);

	# Delete recipe entries and the category itself for each one
	for $branch (0 .. $#tree) {
		&DeleteAllRecipesFromCategory($tree[$branch]->{'category_id'});
		$sth = &ExecSQL(
			"DELETE FROM categories " .
			"WHERE category_id=" . $tree[$branch]->{'category_id'}
			);
	}

	# Do it again for this category - if we use the parent of this one,
	# all other categories at this level will be deleted as well.
	&DeleteAllRecipesFromCategory($l_category_id);
	$sth = &ExecSQL(
		"DELETE FROM categories " .
		"WHERE category_id=$l_category_id"
		);
}


#####################################################################
# DeleteAllRecipesFromCategory($category_id)
#
# Deletes all recipe category entries for in category category_id.
#####################################################################
sub DeleteAllRecipesFromCategory() {
	my($l_category_id) = @_;

	$sth = &ExecSQL(
		"DELETE FROM category_entries " .
		"WHERE category_id=$l_category_id"
		);
}

# END category_editor.cgi
