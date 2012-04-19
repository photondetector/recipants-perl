#!/usr/bin/perl

###########################################################################
# File      : sysinfo.cgi
# Purpose   : System information and statistics
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

require "librecipants.pl";

# _____ GLOBAL VARIABLES ____________________________________________

$cmd = lc(param('cmd'));

# _____ END GLOBAL VARIABLES ________________________________________


&InitUser();	# Set up user info

# Are we logged in?
unless($logged_in) {
	&PrintErrorExit($ls_must_be_signed_in{$language});
}

# Verify access
unless(&UserHasPermission($user_id, $perm_all_access)) {
	&PrintErrorExit($ls_no_perm_stats{$language});
}

&SystemInfoScreen();

&CleanExit(0);


# _____ FUNCTIONS  __________________________________________________

#####################################################################
# SystemInfoScreen()
#
# Displays a page of system stats.
#####################################################################
sub SystemInfoScreen() {
	my($row, $output, $normal_users_count, $suspended_user_count,
		$total_user_count, $recipe_count, $category_count,
		$supported_language_list, $language_code, $default_language_formatted,
		$db_name, $db_version, $db_driver);

	# User count
	$sth = &ExecSQL(
		"SELECT status " .
		"FROM users"
		);

	$normal_user_count    = 0;
	$suspended_user_count = 0;

	while($row = $sth->fetchrow_hashref) {
		if($row->{'status'} == $user_status_normal) {
			$normal_user_count++;
		} else {
			$suspended_user_count++;
		}
	}

	$total_user_count = $normal_user_count + $suspended_user_count;

	# Recipe count
	$sth = &ExecSQL(
		"SELECT COUNT(recipe_id) AS recipe_count " .
		"FROM recipes"
		);

	if($row = $sth->fetchrow_hashref) {
		$recipe_count = $row->{'recipe_count'};
	} else {
		$recipe_count = 0;
	}

	# Category count
	$sth = &ExecSQL(
		"SELECT COUNT(category_id) AS category_count " .
		"FROM categories"
		);

	if($row = $sth->fetchrow_hashref) {
		$category_count = $row->{'category_count'};
	} else {
		$category_count = 0;
	}

	# Readable supported languages
	foreach $language_code (sort(keys(%language_code_map))) {
		$supported_language_list .= $language_code_map{$language_code} .
			" ($language_code)<BR>\n";
	}
	$supported_language_list =~ s/(<BR>) $/$1/;	# trim trailing <BR>

	$default_language_formatted = $language_code_map{$default_language} .
		" ($default_language)";

	# DB info
	$db_driver  		= $dbh->{Driver}->{Name};
	$db_driver_version  = $dbh->{Driver}->{Version};

	# Template time!
	$output = &GetTemplate("system_stats.html");

	# App config
	$output =~ s/REP_APP_NAME/$app_name/g;
	$output =~ s/REP_APP_VERSION/$app_version/g;
	$output =~ s/REP_APP_URL/$app_url/g;
	$output =~ s/REP_APP_HOST_TITLE/$app_host_title/g;
	$output =~ s/REP_APP_HOST_URL/$app_host_url/g;
	$output =~ s/REP_APP_INSTALLED_URL/$app_installed_url/g;
	$output =~ s/REP_COOKIE_DOMAIN/$cookie_domain/g;
	$output =~ s/REP_COOKIE_PATH/$cookie_path/g;
	$output =~ s/REP_SUPPORTED_LANGUAGES/$supported_language_list/g;
	$output =~ s/REP_DEFAULT_LANGUAGE/$default_language_formatted/g;

	# Stuff in the DB - recipes, categories, users
	$output =~ s/REP_TOTAL_USERS/$total_user_count/g;
	$output =~ s/REP_NORMAL_USERS/$normal_user_count/g;
	$output =~ s/REP_SUSPENDED_USERS/$suspended_user_count/g;
	$output =~ s/REP_RECIPES/$recipe_count/g;
	$output =~ s/REP_CATEGORIES/$category_count/g;
	$output =~ s/REP_NORMAL_USERS/$normal_user_count/g;

	# Environment
	$output =~ s/REP_OS_NAME/$^O/g;
	$output =~ s/REP_PERL_VERSION/$]/g;
	$output =~ s/REP_DB_NAME/$db_name/g;
	$output =~ s/REP_DB_VERSION/$db_version/g;
	$output =~ s/REP_DB_DRIVER_NAME/$db_driver/g;
	$output =~ s/REP_DB_DRIVER_VERSION/$db_driver_version/g;

	&ShowPage($ls_system_stats_title{$language}, $output);
}

# END sysinfo.cgi
