###########################################################################
# File      : librecipants.pl
# Purpose   : Library of functions and globals used in > 1 CGI.
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


# Email config defines. These are up here because they need to be defined
# before figuring out if we need to use Net::SMTP.
$send_email_method_smtp     = 0;
$send_email_method_sendmail = 1;

use DBI;
use CGI qw(:cgi);
use Digest::SHA1 qw(sha1_base64);
use MIME::Base64;
# use Net::SMTP if necessary
if($send_email_method == $send_email_method_smtp) {
	use Net::SMTP;
}

require "localized_strings.pl";
require "recipants.cfg.pl";

# Set some reasonable protective defaults
$CGI::POST_MAX        = 1024 * 500;
$CGI::DISABLE_UPLOADS = 1;

# _____ GLOBAL VARIABLES ____________________________________________

$dbh;			# database connection handle
$sth;			# database statement handle
@tree;			# category tree
$success = 1;	# duh
$error   = -1;	# ditto

# User info globals. These are set by InitUser();
$logged_in = 0;		# flag, defaulted to false
$user_name = "";	
$user_id;
$language;			# current language pref
$theme;				# current theme pref


##### CHEESE ALERT! #################################################
# Hard-coded reference data mappings. This sucks according to DB 
# methodology, but it's fast and it'll work for now. These may be
# turned into objects later so that they can read from the DB once
# and persist. This isn't really all that bad as the values are
# explicitly defined in the DML that populates the reference tables
# in the first place, so a deliberate and unnecessary change is
# required to screw this up.
#####################################################################
%ingredient_types = (
	normal      => 1,
	subheading  => 2,
	divider     => 3,
	link        => 4,
);

%unit_map_abbr2id = (
	tsp		=> 1,
	tbsp	=> 2,
	c		=> 3,
	pt		=> 4,
	qt		=> 5,
	gal		=> 6,
	ml		=> 7,
	l		=> 8,
	oz		=> 9,
	floz	=> 10,
	g		=> 11,
	kg		=> 12,
	pinches	=> 13,
	ea		=> 14,
	lb		=> 15,
);

%unit_map_id2abbr = (
	1	=> tsp,
	2	=> TBSP,
	3	=> c,
	4	=> pt,
	5	=> qt,
	6	=> gal,
	7	=> ml,
	8	=> l,
	9	=> oz,
	10	=> floz,
	11	=> g,
	12	=> kg,
	13	=> pi,
	14	=> ea,
	15	=> lb,
);

# Don't remove spaces after single-character abbreviations, they're
# there for a reason.
%unit_map_id2meal_master = (
	1	=> ts,
	2	=> tb,
	3	=> 'c ',
	4	=> pt,
	5	=> qt,
	6	=> ga,
	7	=> ml,
	8	=> 'l ',
	9	=> oz,
	10	=> fl,
	11	=> g,
	12	=> kg,
	13	=> pn,
	14	=> ea,
	15	=> lb,
);

%unit_map_id2name = (
	1	=> Teaspoons,
	2	=> Tablespoons,
	3	=> Cups,
	4	=> Pints,
	5	=> Quarts,
	6	=> Gallons,
	7	=> Mililiters,
	8	=> Liters,
	9	=> Ounces,
	10	=> 'Fluid ounces',
	11	=> Grams,
	12	=> Kilograms,
	13	=> Pinches,
	14	=> Each,
	15	=> Pounds,
);

# User status codes
$user_status_normal     = 1;
$user_status_suspended  = 2;

# User access codes
$perm_all_access        = 0;
$perm_delete_any_recipe = 1;
$perm_edit_any_recipe   = 2;
$perm_edit_any_category = 3;


# _____ FUNCTIONS ___________________________________________________


# _____ USER FUNCTIONS ______________________________________________

#####################################################################
# InitUser()
#
# Attempts to read cookies and set up the user info globals
# accordingly. This function should always be called before anything
# else is done.
#####################################################################
sub InitUser() {
	my($encoded_user_info, $user_info, $cookie_language,
		$supported_language, $language_found);

	# Get language cookie and intelligently set $language global
	if($cookie_language = cookie('rp_language')) {

		# Make sure we support the language
		foreach $supported_language (@supported_languages) {
			if($cookie_language eq $supported_language) {
				$language       = $cookie_language;
				$language_found = 1;
				last;
			}
		}
	}

	# Set default language if we have no cookie or a cookie with
	# an unsupported language.
	unless($language_found) {
		$language = $default_language;
	}

	# Get and authenticate user info from signed cookie and set globals
	if($encoded_user_info = cookie('rp_user')) {
		if($user_info = &CookieDecodeAuthenticate($encoded_user_info)) {
			$logged_in = 1;
			$user_name = $user_info->{'user_name'};
			$user_id   = $user_info->{'user_id'};
		} else {
			&PrintErrorExit($ls_bad_cookie{$language});
		}
	}
}


#####################################################################
# GetUserInfo($user_id)
#
# Returns a reference to a hash containing all of user $user_id's
# base info (everything in the USERS table).
#####################################################################
sub GetUserInfo() {
	my($l_user_id) = @_;
	my($row);

	$sth = &ExecSQL(
		"SELECT user_name, password, email, email_private, url, status, create_utime " .
		"FROM users " .
		"WHERE user_id=$l_user_id"
		);

	if($row = $sth->fetchrow_hashref) {
		return($row);
	} else {
		return(0);
	}
}


# _____ SCREEN & TEMPLATE FUNCTIONS _________________________________

#####################################################################
# ShowPage($page_title, $content, @cookies)
#
# Displays a complete page of HTML with appropriate navigaton.
# Prints the page_head.html template, followed by $content, followed
# by the page_foot.html template. Use this function for display of
# all HTML pages.
#
# This function will figure out if a user is logged in and what (if
# any) administrative actions they can perform and display links
# and login/logout options accordingly.
#
# Cookies need to be set here.
#####################################################################
sub ShowPage() {
	my($page_title, $content, @cookies) = @_;
	my($page_head, $page_foot, $main_menu, $user_menu, $language_menu,
		$admin_menu);

	if($page_title eq "") {
		$page_title = "$app_name v$app_version \@ $app_host_title";
	}

	# Get the page head and fill out the appropriate stuff
	$page_head = &GetTemplate("page_head.html");
	$page_head =~ s/REP_PAGE_TITLE/$page_title/g;
	$page_head =~ s/REP_APP_VERSION/$app_version/g;
	$page_head =~ s/REP_APP_URL/$app_url/g;
	$page_head =~ s/REP_APP_HOST_URL/$app_host_url/g;
	$page_head =~ s/REP_APP_HOST_TITLE/$app_host_title/g;

	# Display the correct main & user menus
	if($logged_in) {
		$main_menu = &GetTemplate("main_nav_logged_in.html");
		$main_menu =~ s/REP_USER_NAME/$user_name/g;

		$user_menu = &GetTemplate("user_nav_logged_in.html");
		$user_menu =~ s/REP_USER_NAME/$user_name/g;
	} else {
		$main_menu = &GetTemplate("main_nav_not_logged_in.html");
		$user_menu = &GetTemplate("user_nav_not_logged_in.html");
	}

	$page_head =~ s/REP_MAIN_MENU/$main_menu/g;
	$page_head =~ s/REP_USER_MENU/$user_menu/g;

	# Language menu, if we have a choice of languages
	if($#supported_languages > 0) {
		$language_menu = &GetLanguageMenu();
	} else {
		$language_menu = "";
	}

	$page_head =~ s/REP_USER_LANGUAGE_MENU/$language_menu/g;

	# Admin menu, anyone? If the user is logged in, get user's permissions
	# and display links to administrative actions that they can perform.
	if($logged_in) {

		# Edit users?
		if(&UserHasPermission($user_id, $perm_edit_any_user)) {
			$admin_menu_options .= "<A HREF=\"user_editor.cgi\">" .
			$ls_edit_users{$language} . "</A><BR>\n";
		} 

		# Edit categories?
		if(&UserHasPermission($user_id, $perm_edit_any_category)) {
			$admin_menu_options .= "<A HREF=\"category_editor.cgi\">" .
			$ls_edit_categories{$language} . "</A><BR>\n";
		}

		# View system info?
		if(&UserHasPermission($user_id, $perm_all_access)) {
			$admin_menu_options .= "<A HREF=\"sysinfo.cgi\">" .
			$ls_view_system_info{$language} . "</A><BR>\n";
		}

		# Strip the last line break as we don't have any real way to count
		$admin_menu_options =~ s/<BR>\n$//;

		# If we have any admin options, get the admin menu template
		if($admin_menu_options) {
			$admin_menu = &GetTemplate("admin_menu.html");
		}

		$admin_menu =~ s/REP_MENU_OPTIONS/$admin_menu_options/g;
	}

	$page_head =~ s/REP_ADMIN_MENU/$admin_menu/g;

	# Do page footer
	$page_foot = &GetTemplate("page_foot.html");

	# Set cookies if we got any
	if($#cookies < 0) {
		print header('text/html');
	} else {
		print header(-type => 'text/html', -cookie => @cookies);
	}

	print $page_head, $content, $page_foot;
}


#####################################################################
# GetTemplate($file_name)
#
# Returns the contents of a template file. Automagically gets the
# file in the correct language for the user.
#####################################################################
sub GetTemplate() {
	my($file_name) = @_;
	my($file_path, $template);

	# Build path based on the global language preference variable
	# set by InitUser()
	$file_path = $template_root_directory . $path_separator . $language .
		$path_separator . $file_name;

	open(GET_TEMPLATE_FILE, "<$file_path") || 
		return($cant_get_template{$language} . " $file_name: $!\n");
	while(<GET_TEMPLATE_FILE>) {
		$template .= $_;
	}
	close(GET_TEMPLATE_FILE);

	return($template);
}


#####################################################################
# PrintError($message)
#
# Prints an error message.
#####################################################################
sub PrintError() {
	my($message) = @_;
	my($output);

	unless($message) {
		$message = $unknown_error{$language};
	}

	$output = &GetTemplate("error_box.html");
	$output =~ s/REP_MESSAGE/$message/g;

	&ShowPage($ls_error_title{$language}, $output);
}


#####################################################################
# PrintErrorExit($message)
#
# Prints an error message, cleans up database stuff, and exits
# the program.
#####################################################################
sub PrintErrorExit() {
	my($message) = @_;

	&PrintError($message);
	&CleanExit(-1);
}


#####################################################################
# PrintSuccess($message)
#
# Prints a success message.
#####################################################################
sub PrintSuccess() {
	my($message) = @_;
	my($output);

	unless($message) {
		$message = $unknown_success{$language};
	}

	$output = &GetTemplate("success_box.html");
	$output =~ s/REP_MESSAGE/$message/g;

	&ShowPage($ls_success_title{$language}, $output);
}


#####################################################################
# PrintSuccessExit($message)
#
# Prints a success message, cleans up database stuff, and exits
# the program.
#####################################################################
sub PrintSuccessExit() {
	my($message) = @_;

	&PrintSuccess($message);
	&CleanExit(0);
}


# _____ COOKIE SIG FUNCTIONS ________________________________________

#####################################################################
# CookieEncodeSign(%hash)
#
# Takes a hash, coverts it to a string using EncodeHashToString(),
# signs it with an SHA-1 hash of the encoded string plus the secret 
# host key, and base64-encodes the whole thing. Returns the encoded,
# signed string.
#
# The only forbidden value for a name field is 'digest' as this is
# what the function uses to place the SHA-1 digest in.
#
# Use the returned string for the value field of your cookie. To
# decode and authenticate the value, call CookieDecodeAuthenticate().
#####################################################################
sub CookieEncodeSign() {
	my(%vals) = @_;
	my($val_string, $digest);

	$val_string = &EncodeHash2String(%vals);

	# Get digest for var string + secret and glue it on
	$digest = sha1_base64($val_string, $secret_host_key);
	$val_string .= "digest=$digest";

	$val_string = encode_base64($val_string);
	return($val_string);
}


#####################################################################
# CookieDecodeAuthenticate($encoded_string)
#
# Takes a string generated by CookieEncodeSign(), verifies the
# signature, and returns a reference to a hash with the encoded
# name-val pairs, including the SHA-1 digest (hash key 'digest').
# 
# Returns a hashref on success (auth OK), 0 on failure (auth failed).
#####################################################################
sub CookieDecodeAuthenticate() {
	my($val_string) = @_;
	my($vals);

	$val_string = decode_base64($val_string);

	$vals = &DecodeString2Hash($val_string);

	# Verify sig - chop off "digest=<digest>", get hash, and compare
	$val_string_no_digest = $val_string;
	$val_string_no_digest =~ s/([\w\W]+)digest=[\w\W]+$/$1/;

	$digest = sha1_base64($val_string_no_digest, $secret_host_key);

	if($digest eq $vals->{'digest'}) {
		return($vals);
	} else {
		return(0);
	}
}


#####################################################################
# EncodeHash2String(%hash)
#
# Encodes a hash to a string, CGI-style (key=val&key=val&). Leaves
# a trailing '&' because we're going to glue the digest=digets_val
# pair on anyway. Returns the encoded string.
#####################################################################
sub EncodeHash2String() {
	my(%vals) = @_;
	my($string);

	# Encode hash to string, CGI-style
	foreach $key (keys(%vals)) {
		$string .= "$key=$vals{$key}&";
	}

	return($string);
}


#####################################################################
# DecodeString2Hash($string)
#
# Decodes a string encoded with EncodeHash2String() back to a hash,
# CGI-style (key=val&key=val&). Returns a hashref.
#####################################################################
sub DecodeString2Hash() {
	my($string) = @_;
	my($vals, $pair, $key, $val);

	# Rebuild hash from key=val pairs
	foreach $pair (split(/&/, $string)) {
		($key, $val)  = split(/=/, $pair);
		$vals->{$key} = $val;
	}

	return($vals);
}


# _____ LANGUAGE FUNCTIONS __________________________________________

#####################################################################
# GetLanguageSelectList()
#
# Returns an HTML SELECT list of available languages with the
# current language selected.
#####################################################################
sub GetLanguageSelectList() {
	my($output, $language_code);

	$output = "<SELECT NAME=\"language\">\n";

	# Build SELECT list from available languages global
	foreach $language_code (keys(%language_code_map)) {
		$output .= "\t\t\t\t\t<OPTION VALUE=\"$language_code\"";

		# Select the current language
		if($language_code eq $language) {
			$output .= " SELECTED";
		}

		$output .= ">" . $language_code_map{$language_code} . "</OPTION>\n";
	}

	$output .= "\t\t\t\t</SELECT>";

	return($output);
}


#####################################################################
# GetLanguageMenu()
#
# Returns a chunk of HTML containing the menu to change languages.
#####################################################################
sub GetLanguageMenu() {
	my($output, $language_select_list);

	$language_select_list = &GetLanguageSelectList();
	$output               = &GetTemplate("user_language_menu.html");
	$output               =~ s/REP_LANGUAGE_SELECT_LIST/$language_select_list/g;

	return($output);
}


# _____ DATABASE FUNCTIONS __________________________________________

#####################################################################
# DBConnect()
#
# Connects to the database and returns a DB connection handle. Exits
# displaying an error if it can't connect.
#####################################################################
sub DBConnect() {
	my $dbh = DBI->connect (
		"dbi:$db_driver:dbname=$db_name",
		$db_uname,
		$db_passwd
		) || &PrintErrorExit($ls_cant_connect_to_database{$language} . $DBI::errstr);
	
	return($dbh);
}


#####################################################################
# ExecSQL($dbh, $sql)
#
# Executes a SQL statement. Prints an error and exits upon DB error;
# returns a statement handle on success.
#
# This function connects to the database if necessary, so don't
# explicitly call DBConnect() yourself.
#####################################################################
sub ExecSQL() {
	my($sql) = @_;
	my($statement_handle);

	# Connect to the database if necessary.
	unless($dbh->{Active}) {
		$dbh = &DBConnect();
	}

	# Prepare statement
	unless($statement_handle = $dbh->prepare($sql)) {
		&PrintErrorExit($cant_prepare_sql{$language} . $dbh->errstr());
	}

	# Execute statement
	unless($statement_handle->execute()) {
		&PrintErrorExit($cant_execute_sql{$language} . $dbh->errstr() . 
			"<BR><BR>SQL: <CODE><B>$sql</B></CODE>");
	}

	return($statement_handle);
}


#####################################################################
# DBEscapeString($string)
#
# Escapes a string for use in a SQL statement.
#####################################################################
sub DBEscapeString() {
	my($string) = @_;

	$string =~ s/\'/\'\'/g; # ' -> ''
	$string =~ s/\</&lt;/g; # HTML-escape less-than
	$string =~ s/\>/&gt;/g; # HTML-escape greater-than

	return($string);
}


# _____ COMMON RECIPE FUNCTIONS _____________________________________

#####################################################################
# GetRecipeIngredients($recipe_id)
#
# Gets ingredients for recipe recipe_id. Returns an array of hashes.
#####################################################################
sub GetRecipeIngredients() {
	my($l_recipe_id, $scale_factor) = @_;
	my(%row, @ingredients, %this_ingredient, %scaled);

	# Get data from DB
	$sth = &ExecSQL(
		"SELECT u.unit_id, ing.name, ing.qty, u.abbreviation " .
		"FROM ingredients ing, units u " .
		"WHERE ing.recipe_id=$l_recipe_id AND u.unit_id=ing.unit_id " .
		"ORDER BY ing.display_order"
		);

	# Scale then format qty val from decimal to fraction and glue a ref
	# to each hash (db row) we get on to @ingredients
	while($row = $sth->fetchrow_hashref) {
		$this_ingredient = {};
		$this_ingredient->{'name'}    = $row->{'name'};
		$this_ingredient->{'unit_id'} = $row->{'unit_id'};

		# Scale
		if($scale_factor ne "" && $scale_factor != 1 && $scale_factor > 0) {
			%scaled = {};
			%scaled = &ScaleIngredient($row->{'qty'}, $row->{'abbreviation'}, $scale_factor);
			$this_ingredient->{'qty'}          = %scaled->{'qty'};
			$this_ingredient->{'abbreviation'} = %scaled->{'unit'};
		} else {
			$this_ingredient->{'qty'}          = $row->{'qty'},
			$this_ingredient->{'abbreviation'} = $row->{'abbreviation'};
		}	

		$this_ingredient->{'qty'} = frac($this_ingredient->{'qty'}, MIXED);
		push @ingredients, $this_ingredient;
	}

	if($#ingredients < 0) {
		@ingredients = ();
	}

	return(@ingredients);
}


####################################################################
# GetRecipeBaseInfo($recipe_id)
#
# Gets basic recipe info from the DB (RECPIES table). Returns a hash.
#####################################################################
sub GetRecipeBaseInfo() {
	my($l_recipe_id) = @_;
	my($row);

	# Get data from DB
	$sth = &ExecSQL(
		"SELECT r.name, r.yield_qty, r.yield_units, r.source, r.author_user_id, u.user_name " .
		"FROM recipes r, users u " .
		"WHERE recipe_id=$l_recipe_id " .
		"AND u.user_id=r.author_user_id"
		);
	
	# Process results
	if($row = $sth->fetchrow_hashref) {
		return($row);
	} else {
		&PrintErrorExit("GetRecipeBaseInfo($l_recipe_id): " . $ls_cant_find_recipe{$language});
	}
}


#####################################################################
# GetRecipeInstructions($recipe_id)
#
# Gets recipe instructions for recipe recipe_id. Returns an array.
#####################################################################
sub GetRecipeInstructions() {
	my($l_recipe_id) = @_;
	my($row, @instructions);

	# Get data from DB
	$sth = &ExecSQL(
		"SELECT step_num, step_text " .
		"FROM instructions " .
		"WHERE recipe_id=$l_recipe_id " .
		"ORDER BY step_num"
		);

	# Add each row to the array as a new element
	while($row = $sth->fetchrow_hashref) {
		push(@instructions, $row->{'step_text'});
	}

	return(@instructions);
}


#####################################################################
# GetRecipesEnteredByUser($user_id)
#
# Returns a list of hashes containing the recipe_id and name of each
# recipe entered by $user_id.
#####################################################################
sub GetRecipesEnteredByUser() {
	my($l_user_id) = @_;
	my($row, @recipes);

	$sth = &ExecSQL(
		"SELECT recipe_id, name " .
		"FROM recipes " .
		"WHERE author_user_id=$l_user_id " .
		"ORDER BY name"
		);

	while($row = $sth->fetchrow_hashref) {
		push(@recipes, $row);
	}

	if($#recipes < 0) {
		@recipes = ();
	}

	return(@recipes);
}


#####################################################################
# GetRecipesEnteredByUserHTML($user_id)
#
# Returns a chunk of HTML containing links to the recipes entered by
# by user $user_id.
#####################################################################
sub GetRecipesEnteredByUserHTML() {
	my($l_user_id) = @_;
	my(@recipes, $recipe_number, $output);

	@recipes = &GetRecipesEnteredByUser($l_user_id);

	# Add leading SPAN tag if we got any recipes
	if($#recipes >= 0) {
		$output = "<SPAN CLASS=\"recipe-link\">\n";
	}

	foreach $recipe_number (0 .. $#recipes) {
		$output .= "\t\t<A HREF=\"recipe.cgi?recipe_id=" .
			$recipes[$recipe_number]->{'recipe_id'} . "\">" . 
			$recipes[$recipe_number]->{'name'} . "</A>";

		# Line break if we aren't last
		if($recipe_number < ($#recipes)) {
			$output .= "<BR>\n";
		}
	}

	# closing span tag
	if($#recipes >= 0) {
		$output .= "\n</SPAN>";
	}

	return($output);
}


# _____ SCALING AND CONVERSION ______________________________________

#####################################################################
# ScaleIngredient($qty, $unit, $scale_factor)
#
# Scales a quantity by $scaleFactor. Units may be diferent on the
# way out than on the way in, e.g. ScaleIngredient(1, "cup", 4) will
# return $result{"qty"} = 1, $result{"unit"} = "quart".
#####################################################################
sub ScaleIngredient {
	my($qty, $unit, $scale_factor) = @_;
	my(%result);

	$result{'qty'}  = $qty * $scale_factor;
	$result{'unit'} = $unit;

	return(%result);
}


# _____ CATEGORIES __________________________________________________

#####################################################################
# GetCategoryInfo($category_id)
#
# Returns a hash of category_id, parent, and name for category
# $category_id.
#####################################################################
sub GetCategoryInfo() {
	my($l_category_id) = @_;
	my($row);

	$sth = &ExecSQL(
	 	"SELECT category_id, parent, name " .
		"FROM categories " .
		"WHERE category_id=$l_category_id"
		);

	if($row = $sth->fetchrow_hashref) {
		return($row);
	} else {
		$row = {};
		return($row);
	}
}


#####################################################################
# GetSubcategories($category_id)
#
# Returns a list of hashes of category info that are subcategories of
# $category_id.
#####################################################################
sub GetSubcategories() {
	my($l_category_id) = @_;
	my(@subs, $row);

	$sth = &ExecSQL(
		"SELECT category_id, name " .
		"FROM categories " .
		"WHERE parent=$l_category_id " . 
		"ORDER BY name"
		);

	# Push row onto our list
	while($row = $sth->fetchrow_hashref) {
		push(@subs, $row);
	}

	if($#subs < 0) {
		@subs = ();
	}

	return(@subs);
}


#####################################################################
# GetSubcategoriesHTML($category_id)
#
# Returns an HTML chunk of links to subcategories of $category_id.
#####################################################################
sub GetSubcategoriesHTML() {
	my($l_category_id) = @_;
	my(@subs, $sub_num, $output);

	@subs = &GetSubcategories($l_category_id);

	for $sub_num (0 .. $#subs) {
		$output .= "<SPAN CLASS=\"subcategory-link\">" .
		"<A HREF=\"category.cgi?category_id=" .
		$subs[$sub_num]->{'category_id'} . "\">" . $subs[$sub_num]->{'name'} .
		"</A></SPAN><BR>\n";
	}

	return($output);
}


#####################################################################
# UserHasRecipeBookmarked($user_id, $recipe_id)
#
# Checks to see if recipe $recipe_id in is user $user_id's recipe
# bookmarks list.
#
# Returns 1 if true, 0 if false.
#####################################################################
sub UserHasRecipeBookmarked() {
	my($l_user_id, $l_recipe_id) = @_;
	my($row);

	$sth = &ExecSQL(
		"SELECT recipe_id " .
		"FROM user_recipe_bookmarks " .
		"WHERE user_id=$user_id " .
			"AND recipe_id=$l_recipe_id"
		);

	if($row = $sth->fetchrow_hashref) {
		return(1);
	} else {
		return(0);
	}
}


# _____ CATEGORY BREADCRUMBS ________________________________________

#####################################################################
# GetCategoryBreadcrumbs($category_id, $include_top_category)
#
# Returns an ordered array of hashes containing category info for
# each crumb.
#
# i.e.
#
# @breadcrumbs[0]->{'category_id'} == 14
# @breadcrumbs[0]->{'parent'}      == 0
# @breadcrumbs[0]->{'name'}        == Desserts
#
# @breadcrumbs[1]->{'category_id'} == 29
# @breadcrumbs[1]->{'parent'}      == 14
# @breadcrumbs[1]->{'name'}        == Cakes
#
# @breadcrumbs[2]->{'category_id'} == 304
# @breadcrumbs[2]->{'parent'}      == 29
# @breadcrumbs[2]->{'name'}        == Chocolate
#####################################################################
sub GetCategoryBreadcrumbs() {
	my($l_category_id, $include_top_category) = @_;
	my(%this_crumb, @breadcrumbs, $this_category_id);

	# Keep getting parent entries as long as we can
	for($this_category_id = $l_category_id; $this_category_id >= 0; $this_category_id = $this_crumb->{'parent'}) {
		%this_crumb = {};
		$this_crumb = &GetCategoryInfo($this_category_id);

		unless($include_top_category == 0 && $this_category_id == 0) {
			push(@breadcrumbs, $this_crumb);
		}
	}

	# If we got anything, reverse @breadcrumbs to put higest level first
	if($#breadcrumbs >= 0) {
		@breadcrumbs = reverse(@breadcrumbs);
	} else {
		@breadcrumbs = ();
	}

	return(@breadcrumbs);
}


#####################################################################
# GetCategoryBreadcrumbsHTML($category_id, $link_last, $include_top_category)
#
# Returns a chunk of HTML containing the breadcrumb nav for $category_id.
#####################################################################
sub GetCategoryBreadcrumbsHTML() {
	my($l_category_id, $link_last, $include_top_category) = @_;
	my(%this_crumb, $this_category_id);

	@this_trail = &GetCategoryBreadcrumbs($l_category_id, $include_top_category);

	for $crumb_number (0 .. $#this_trail) {
		$this_category_id = $this_trail[$crumb_number]->{'category_id'};
		$name             = $this_trail[$crumb_number]->{'name'};

		if($crumb_number == 0) {					# Add leading SPAN tag if we're first
			$trail_formatted = "<SPAN CLASS=\"category-breadcrumb\">";
		}

		if($crumb_number <= ($#this_trail - 1)) {	# Add category separator if we're not last
			$trail_formatted  .= "<A HREF=\"category.cgi?category_id=$this_category_id\">$name</A> &gt; ";
		} else {
			if($link_last != 0) {					# Add closing SPAN tag if we are last
				$trail_formatted .= "<A HREF=\"category.cgi?category_id=$this_category_id\">$name</A>";
			} else {
				$trail_formatted .= $name;
			}
			$trail_formatted .= "</SPAN>\n";
		}
	}

	return($trail_formatted);
}


#####################################################################
# GetCategoryBreadcrumbsForRecipe($recipe_id)
#
# Returns an array of arrays of hashes. See GetCategoryBreadcrumbs()
# for more info.
#####################################################################
sub GetCategoryBreadcrumbsForRecipe() {
	my($l_recipe_id) = @_;
	my(@categories, $ctr, @breadcrumbs, @this_breadcrumb);

	@categories = &GetCategoriesForRecipe($l_recipe_id);
	if($#categories < 0) {
		@categories = ();
		return(@categories);
	}

	$num_crumbs = 0;
	for $ctr (0 .. $#categories) {
		@this_breadcrumb = &GetCategoryBreadcrumbs($categories[$ctr], 0);
		push(@breadcrumbs, @this_breadcrumb);
		$num_crumbs++;
	}

	if($num_crumbs == 0) {
		@breadcrumbs = ();
	}

	return(@breadcrumbs);
}


#####################################################################
# GetCategoryBreadcrumbsForRecipeHTML($recipe_id)
#
# Returns an array of HTML, one element of breadcrumbs per category.
#####################################################################
sub GetCategoryBreadcrumbsForRecipeHTML() {
	my($l_recipe_id, $link_last) = @_;
	my(@categories, @trails, @this_trail, $trail_formatted, $name, $category_id);

	$num_trails = 0;
	@categories = &GetCategoriesForRecipe($l_recipe_id);

	foreach $category (@categories) {
		$trail_formatted = &GetCategoryBreadcrumbsHTML($category, $link_last);
		push @trails, $trail_formatted;
	}

	if($#trails < 0) {
		push(@trails, $ls_recipe_in_no_categories{$language});
	}
	return(@trails);
}


# _____ CATEGORY TREE _______________________________________________

#####################################################################
# GetCategoryTree($parent_category_id, $level)
#
# This function written by Ben Mehlman.
#
# Populates the global @tree with the category tree in hashes. Each
# hash contains the category_id, name, and level.
#
# As this function is recursive and it treats @tree like a stack,
# you should re-set @tree before calling this function.
#####################################################################
sub GetCategoryTree() {
	my($parent_key, $level) = @_;
	my(@subs, $sub_num, %this_category);

	# This should never happen but if data in database forms a loop
	# it would cause program to suck up as much memory as it could get!
	return(0) if($level > $max_category_depth);

	@subs = &GetSubcategories($parent_key);
	for $sub_num (0 .. $#subs) {
		%this_category = {};
		$this_category = $subs[$sub_num];
		$this_category->{'level'} = $level;
		push(@tree, $this_category);

		&GetCategoryTree($subs[$sub_num]->{'category_id'}, $level + 1);
	}
}


#####################################################################
# GetCategoryTreeCheckboxes()
#
# Returns a chunk of HTML containing the category tree as form
# elements with checkboxes next to each branch (doesn't include
# opening or closing FORM tags). Each checkbox has a form submission
# value of its category_id.
#####################################################################
sub GetCategoryTreeCheckboxes() {
	my($output);

	@tree = ();
	&GetCategoryTree(0, 0);

	$output = "<SPAN CLASS=\"category-tree\">\n";

	for $branch (0 .. $#tree) {
		# If we're a top-level and we aren't first, add a line break
		if($tree[$branch]->{'level'} == 0 && $branch != 0) {
			$output .= "<BR>\n";
		}

		$output .= "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;" x $tree[$branch]->{'level'};
		$output .= "<INPUT TYPE=\"checkbox\" NAME=\"categories\" " .
			"VALUE=\"" . $tree[$branch]->{'category_id'} . "\"> ";
		$output .= $tree[$branch]->{'name'};
	
		# Add a line break if we're not last
		if($branch != $#tree) {
			$output .= "<BR>";
		}
		$output .= "\n";
	}

	$output .= "</SPAN>\n";
	return($output);
}


#####################################################################
# GetCategoryTreeSelectList()
#
# Returns a chunk of HTML containing the category tree as a SELECT
# (drop-down) form element (doesn't include opening or closing FORM
# tags). Each OPTION has a form submission value of its category_id.
#
# As some pages will need to display the select list more than once
# with different form element names and this function is 
# database-intensive, the element name is returned as 
# REP_ELEMENT_NAME. Call this function once and replace the element
# name as needed.
#####################################################################
sub GetCategoryTreeSelectList() {
	my($start_category_id) = @_;
	my($output);

	@tree = ();
	&GetCategoryTree($start_category_id, 0);

	$output = "<SELECT NAME=\"REP_ELEMENT_NAME\">\n";

	for $branch (0 .. $#tree) {
		$output .= "\t<OPTION VALUE=\"" . $tree[$branch]->{'category_id'} . "\">";
		$output .= "&nbsp;&nbsp;&nbsp;&nbsp;" x $tree[$branch]->{'level'};
		$output .= $tree[$branch]->{'name'} . "</OPTION>\n";
	}

	$output .= "</SELECT>\n";
	return($output);
}


#####################################################################
# GetCategoryTreeLinks()
#
# Returns a chunk of HTML containing the category tree. Each branch
# contains a link to display its category
# (category.cgi?category_id=$category_id).
#####################################################################
sub GetCategoryTreeLinks() {
	my($output);

	@tree = ();
	&GetCategoryTree(0, 0);

	for $branch (0 .. $#tree) {
		# If we're a top-level and we aren't first, add a line break
		if($tree[$branch]->{'level'} == 0 && $branch != 0) {
			$output .= "<BR>\n";
		}

		# Indent
		$output .= "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;" x $tree[$branch]->{'level'};
		$output .= "<A HREF=\"category.cgi?category_id=" . 
			$tree[$branch]->{'category_id'} . "\">" .
			$tree[$branch]->{'name'} . "</A>";

		# Add a line break if we're not last
		if($branch != $#tree) {
			$output .= "<BR>";
		}
		$output .= "\n";
	}

	return($output);
}


# _____ RECIPE-CATEGORY STUFF _______________________________________

#####################################################################
# DeleteRecipeCategories($recipe_id)
#
# Deletes all recipe category entries for $recipe_id.
#####################################################################
sub DeleteRecipeCategories() {
	my($l_recipe_id) = @_;

	$sth = &ExecSQL(
		"DELETE FROM category_entries " .
		"WHERE recipe_id=$l_recipe_id"
		);
}


#####################################################################
# GetCategoriesForRecipe($recipe_id)
#
# Returns an array of category_ids that match $recipe_id.
#####################################################################
sub GetCategoriesForRecipe() {
	my($l_recipe_id) = @_;
	my($row, @categories, $this_category_id);

	$sth = &ExecSQL(
		"SELECT category_id " .
		"FROM category_entries " .
		"WHERE recipe_id=$l_recipe_id"
		);

	while($row = $sth->fetchrow_hashref) {
		$this_category_id = $row->{'category_id'};
		push(@categories, $this_category_id);
		$num_categories++;
	}

	if($#categories < 0) {
		@categories = ();
	}

	return(@categories);
}


#####################################################################
# GetRecipesInCategory($category_id)
#
# Returns an hash of key=recipe_id, val=name for recipes in 
# $category_id.
#####################################################################
sub GetRecipesInCategory() {
	my($l_category_id) = @_;
	my($row, %recipes, $this_recipe_id);

	$sth = &ExecSQL(
		"SELECT category_entries.recipe_id, recipes.name " .
		"FROM category_entries, recipes " .
		"WHERE category_entries.category_id=$l_category_id " .
		"AND recipes.recipe_id=category_entries.recipe_id " .
		"ORDER BY recipes.name"
		);

	while($row = $sth->fetchrow_hashref) {
		$this_recipe_id = $row->{'recipe_id'};
		$recipes{$this_recipe_id} = $row->{'name'};
	}

	return(%recipes);
}


# _____ ACCESS CONTROL ______________________________________________

#####################################################################
# GetPermissions($user_id)
#
# Returns a list of permission_ids for user $user_id.
#####################################################################
sub GetPermissions() {
	my($l_user_id) = @_;
	my($row, @permissions);

	$sth = &ExecSQL(
		"SELECT permission_id " .
		"FROM user_access_grants " .
		"WHERE user_id=$l_user_id"
		);

	while($row = $sth->fetchrow_hashref) {
		push(@permissions, $row->{'permission_id'});
	}

	# This kind of check shouldn't be necessary, but sometimes it doesn't
	# work otherwise, so I do this all over the place.
	if($#permissions < 0) {
		@permissions = ();
	}

	return(@permissions);
}


#####################################################################
# UserHasPermission($user_id, $permission_id)
#
# Checks to see if user $user_id has permission $permission_id.
# Returns 1 if true, 0 if false.
#####################################################################
sub UserHasPermission() {
	my($l_user_id, $l_permission_id) = @_;
	my(@permissions, $permission);

	@permissions = &GetPermissions($l_user_id);

	# If we have a match or if the user has All Access permission, return 1
	foreach $permission (@permissions) {
		if($permission == $l_permission_id || $permission == $perm_all_access) {
			return(1);
		}
	}

	# Otherwise return 0
	return(0);
}


# _____ MISC ________________________________________________________

#####################################################################
# GetUnitSelectList()
#
# Returns an HTML form SELECT list containing all available units of
# measure.
#####################################################################
sub GetUnitSelectList() {
	my($list) = "<SELECT NAME=\"unit_id\">\n";
	
	# Get data from DB
	$sth = &ExecSQL(
		"SELECT unit_id, abbreviation " .
		"FROM units"
		);

	while(my $row = $sth->fetchrow_hashref) {
		$list .= "\t<OPTION VALUE=\"$row->{'unit_id'}\">$row->{'abbreviation'}\n";
	}

	return($list . "</SELECT>");
}


#####################################################################
# SendEmail($from_name, $from_email, $to_name, $to_email, $subject, $message)
#
# Email wrapper. Calls either SendEmailSendmail() or SendEmailSMTP()
# depending on user preference.
#####################################################################
sub SendEmail() {
	my($from_name, $from_email, $to_name, $to_email, $subject, $message) = @_;

	if($send_email_method == $send_email_method_smtp) {
		&SendEmailSMTP($from_name, $from_email, $to_name, $to_email, $subject, $message);
	} elsif($send_email_method == $send_email_method_sendmail) {
		&SendEmailSendmail($from_name, $from_email, $to_name, $to_email, $subject, $message);
	} else {
		&PrintErrorExit($ls_no_email_method_defined{$language});
	}
}


#####################################################################
# SendEmailSMTP($from_name, $from_email, $to_name, $to_email, $subject, $message)
#
# Sends an email using an SMTP server.
#####################################################################
sub SendEmailSMTP() {
	my($from_name, $from_email, $to_name, $to_email, $subject, $message) = @_;
	my($smtp);

	$smtp = Net::SMTP->new($smtp_server);

	$smtp->mail($from_email);
	$smtp->to($to_email);
	$smtp->data();
	$smtp->datasend("To: $to_name \<$to_email\>\r\n");
	$smtp->datasend("Subject: $subject\r\n\r\n");
	$smtp->datasend("$message\r\n");
	$smtp->dataend();

	$smtp->quit();
}


#####################################################################
# SendEmailSendmail($from_name, $from_email, $to_name, $to_email, $subject, $message)
#
# Sends an email using sendmail.
#####################################################################
sub SendEmailSendmail() {
	my($from_name, $from_email, $to_name, $to_email, $subject, $message) = @_;

	# Open a pipe to sendmail
	open(SM, "|$sendmail $to_email") or
		&PrintErrorExit("SendEmailSendmail(): " . $ls_cant_open_pipe_to{$language} .
			" <PRE>$sendmail</PRE>: $!");

	print SM "From: $from_name \<$from_email\>\r\n";
	print SM "To: $to_name \<$to_email\>\r\n";
	print SM "Subject: $subject\r\n\r\n";
	print SM "$message\r\n";
	print SM ".\r\n";
	close(SM);
}


#####################################################################
# EmailOK($address)
#
# Checks an email address for correct format.
# Returns 1 for pass, 0 for fail.
#
# I lifted this regex from 
# http://aspn.activestate.com/ASPN/Cookbook/Rx/Recipe/59886
#####################################################################
sub EmailOK() {
	my($address) = @_;

	if($address =~ /^([A-Z0-9]+[._]?){1,}[A-Z0-9]+\@(([A-Z0-9]+[-]?){1,}[A-Z0-9]+\.){1,}[A-Z]{2,4}$/i) {
		return(1);
	} else {
		return(0);
	}
}


#####################################################################
# ltrim($string)
#
# Removes leading whitespace from $string. (Left TRIM, Oracle-style)
# Returns the trimmed value without modifying the input string.
#####################################################################
sub ltrim() {
	my($string) = @_;
	$string =~ s/^\s*//;
	return($string);
}


#####################################################################
# rtrim($string)
#
# Removes trailing whitespace from $string. (Right TRIM, Oracle-style)
# Returns the trimmed value without modifying the input string.
#####################################################################
sub rtrim() {
	my($string) = @_;
	$string =~ s/\s*$//;
	return($string);
}


#####################################################################
# trim($string)
#
# Removes whitespace from the left of $string
# Returns the trimmed value without modifying the original string.
# 
# This regex by Marc Hartstein.
#####################################################################
sub trim() {
	my($string) = @_;
	$string =~ s/^\s*(.*?)\s*$/$1/;
	return($string);
}


#####################################################################
# CleanExit($exit_code)
#
# Cleans up database stuf and exits the program with exit code
# $exit_code.
#####################################################################
sub CleanExit() {
	my($exit_code) = @_;

	# Clean up the global DB statement handle if there is one
	if($sth) {
		$sth->finish(); 
	}

	# Clean up the global DB connection handle if there is one
	if($dbh) {
		$dbh->disconnect();
	}

	exit($exit_code);
}


#####################################################################
# EscapeFileName($raw_rile_name)
#
# Returns string $raw_file_name escaped for use as a file name.
#####################################################################
sub EscapeFileName() {
	my($file_name) = @_;

	# I know a lot of these can be collapsed; this is for clarity
	$file_name =~ s/ /_/g;		# Translate spaces to underscores
	$file_name =~ s/\//\-/g;	# Translate slashes to dashes
	$file_name =~ s/\\/\-/g;	# Translate backslashes to dashes
	$file_name =~ s/\*/\-/g;	# Translate asterisks to dashes
	$file_name =~ s/\?/\-/g;	# Translate question marks to dashes
	$file_name =~ s/\:/\-/g;	# Translate colons to dashes
	$file_name =~ s/\;/\-/g;	# Translate semicolons to dashes
	$file_name =~ s/\%/\-/g;	# Translate percent signs to dashes
	$file_name =~ s/\^/\-/g;	# Translate carets to dashes
	$file_name =~ s/\!/\-/g;	# Translate bangs to dashes
	$file_name =~ s/\|/\-/g;	# Translate pipes to dashes
	$file_name =~ s/\</\-/g;	# Translate less-thans to dashes
	$file_name =~ s/\>/\-/g;	# Translate greater-thans to dashes
	$file_name =~ s/\"//g;		# Ditch double quotes
	$file_name =~ s/'//g;		# Ditch single quotes
	$file_name =~ s/`//g;		# Ditch backticks

	return(&trim($file_name));
}


#####################################################################
# UnixTimeToString($unix_time)
#
# Returns $unix_time as a formatted string.
#####################################################################
sub UnixTimeToString() {
	my($unix_time) = @_;
	my($sec, $min, $hour, $mday, $mon, $year, $wday, $yday, $isdst) = 
		localtime($unix_time);

	$year += 1900;

	# Zero-pad single-length values
	if(length($hour) == 1) { $hour = "0" . $hour; }
	if(length($min)  == 1) { $min  = "0" . $min; }
	if(length($sec)  == 1) { $sec  = "0" . $sec; }

	return("$mday-$mon-$year $hour:$min:$sec");
}


# Return true
1;

# END librecipants.pl
