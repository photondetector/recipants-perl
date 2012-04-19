#!/usr/bin/perl

###########################################################################
# File      : user_editor.cgi
# Purpose   : User admin stuff.
# Program   : ReciPants ( http://recipants.photondetector.com/ )
# Version   : 1.0
# Author    : Nick Grossman <nick@photondetector.com>
# Tab stops : 4
#
# Copyright (c) 2002, 2003
#     Nicolai Grossman <nick@photondetector.com>
#     Benjamin Mehlman <ben_recipe@cownow.com>
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
unless(&UserHasPermission($user_id, $perm_edit_any_user)) {
	&PrintErrorExit($ls_no_perm_edit_users{$language});
}


# What are we doing?
if($cmd eq "search_by_user_name" || $cmd eq "search_by_email") {
	&SearchForUsers();
}
elsif($cmd eq "edit") {
	&EditUserScreen();
}
elsif($cmd eq "save") {
	&SaveUser();
}
else {	# Show search for users screen by default
	&UserSearchScreen();
}


&CleanExit(0);


# _____ FUNCTIONS  __________________________________________________

#####################################################################
# UserSearchScreen($user_name, $email, $results, $message)
#
# Displays the search for users screen, with optional error message
# $message and optional search results $results.
#####################################################################
sub UserSearchScreen() {
	my($l_user_name, $email, $results, $message) = @_;
	my($output, $error_box, $results_template);
	$output = &GetTemplate("user_editor_user_search_form.html");

	# Get the error template and fill it out if we got an error message
	if($message) {
		$error_box = &GetTemplate("error_box.html");
		$error_box =~ s/REP_MESSAGE/$message/g;
		$output    = $error_box . $output;
	}

	$output =~ s/REP_USER_NAME/$l_user_name/g;
	$output =~ s/REP_EMAIL/$email/g;
	&ShowPage("User Editor: Search", $output . $results);
}


#####################################################################
# SearchForUsers()
#
# Searches for users by username or email. Calls UserSearchScreen()
# with a chunk of HTML containing links to edit matching users.
#####################################################################
sub SearchForUsers() {
	my($email, $l_user_name, $row, $user_list, $output, $search_form,
		$num_users_found, $search_term);

	# How are we searching? Check for the right args and do the right query.
	if($cmd eq "search_by_user_name") {
		# Check for arg
		$l_user_name = &DBEscapeString(lc(trim(param('user_name'))));
		unless($l_user_name) {
			&UserSearchScreen("", "", "", $ls_no_search_term{$language});
			return(0);
		}

		$search_term = $l_user_name;

		$sth = &ExecSQL(
			"SELECT user_id, user_name, email " .
			"FROM users " .
			"WHERE user_name_lower LIKE '%$l_user_name%' " .
			"ORDER BY user_name"
			);
	} else {	# Search by email address
		# Check for arg
		$email = &DBEscapeString(lc(trim(param('email'))));
		unless($email) {
			&UserSearchScreen("", "", "", $ls_no_search_term{$language});
			return(0);
		}

		$search_term = $email;

		$sth = &ExecSQL(
		"SELECT user_id, user_name, email " .
			"FROM users " .
			"WHERE LOWER(email) LIKE '%$email%' " .
			"ORDER BY user_name"
			);
	}

	# Process results
	$num_users_found = 0;
	while($row = $sth->fetchrow_hashref) {
		$user_list .= "<A HREF=\"user_editor.cgi?cmd=edit&user_id=" .
			$row->{'user_id'} . "\">" . $row->{'user_name'} . "</A> " .
			"&lt;" . $row->{'email'} . "&gt;<BR>\n";
		$num_users_found++;
	}

	# Did we get any?
	if($user_list) {
		# Remove last newline
		$user_list =~ s/<BR>\n$//g;
	} else {
		$user_list = $ls_no_matching_users{$language};
	}

	# Fill out template and hand it off to UserSearchScreen()
	$output = &GetTemplate("user_admin_user_search_results.html");
	$output =~ s/REP_SEARCH_TERM/$search_term/g;
	$output =~ s/REP_NUM_HITS/$num_users_found/g;
	$output =~ s/REP_RESULTS/$user_list/g;

	&UserSearchScreen($l_user_name, $email, $output);
}


#####################################################################
# EditUserScreen()
#
# Self-explanatory.
#####################################################################
sub EditUserScreen() {
	my($l_user_id, $user_base_info, $private_email_selector, 
		$account_active_selector, $row, $output, @permissions,
		$permission, $create_time, $login_history);

	# Make sure we have a user ID
	$l_user_id = trim(param('user_id'));
	unless($l_user_id) {
		&UserSearchScreen("", "", "", $ls_no_user_id{$language});
		return(0);
	}

	$output = &GetTemplate("user_edit.html");

	# Get user info
	unless($user_base_info = &GetUserInfo($l_user_id)) {
		&PrintErrorExit($ls_user_not_found{$language});
	}

	# Handle Private Email checkbox
	if($user_base_info->{'email_private'} == 1) {
		$private_email_selector = "CHECKED";
	}

	# Handle Account Active checkbox
	if($user_base_info->{'status'} == $user_status_normal) {
		$account_active_selector = "CHECKED";
	}

	# Handle permissions
	@permissions = &GetPermissions($l_user_id);
	foreach $permission (@permissions) {
		$output =~ s/(NAME=\"permissions\" VALUE=\"$permission\")/$1 CHECKED/g;
	}

	$create_time = &UnixTimeToString($user_base_info->{'create_utime'});

	$login_history = &GetLoginHistoryHTML($l_user_id);

	$output =~ s/REP_USER_ID/$l_user_id/g;
	$output =~ s/REP_USER_NAME/$user_base_info->{'user_name'}/g;
	$output =~ s/REP_PASSWORD/$user_base_info->{'password'}/g;
	$output =~ s/REP_EMAIL/$user_base_info->{'email'}/g;
	$output =~ s/REP_PRIVATE_EMAIL/$private_email_selector/g;
	$output =~ s/REP_URL/$user_base_info->{'url'}/g;
	$output =~ s/REP_CREATE_DATE/$create_time/g;
	$output =~ s/REP_ACCOUNT_ACTIVE/$account_active_selector/g;
	$output =~ s/REP_LOGIN_HISTORY/$login_history/g;

	&ShowPage($ls_edit_user{$language} . $user_base_info->{'user_name'}, $output);
}


#####################################################################
# SaveUser()
#
# The name pretty much says it all.
#####################################################################
sub SaveUser() {
	my($l_user_id, $l_user_name, $user_name_lower, $password, $email, 
		$email_lower, $row, $email_private, $url, $status, $permission,
		@permissions, $now_utime);

	$l_user_id = param('user_id');
	unless($l_user_id) {
		&PrintErrorExit($ls_no_user_id{$language});
	}

	$l_user_name     = &DBEscapeString(trim(param('user_name')));
	$user_name_lower = lc($l_user_name);
	$email           = &DBEscapeString(trim(param('email')));
	$password        = &DBEscapeString(trim(param('password')));
	$url             = &DBEscapeString(trim(param('url')));	# URL is not required
	$now_utime       = time();

	# Check for required args
	unless($l_user_name) {
		&PrintErrorExit($ls_missing_user_name{$language});
	}

	unless($email) {
		&PrintErrorExit($ls_missing_user_email{$language});
	}

	# Validate email address length
	if(length($email) > 75) {
		&PrintErrorExit($ls_email_too_long{$language});
	}

	# Validate email address format
	unless(&EmailOK($email)) {
		&PrintErrorExit($ls_bad_email_format{$language});
	}

	# Validate user name length
	if(length($user_name) > 30) {
		&PrintErrorExit($ls_uname_too_long{$language});
	}

	# Verify password length
	if(length($password) < 6 || length($password) > 20) {
		&PrintErrorExit($ls_bad_passwd_length{$language});
	}

	# See if this username is taken by someone else
	$sth = &ExecSQL(
		"SELECT user_id " .
		"FROM users " .
		"WHERE user_name_lower='$user_name_lower'"
		);

	if($row = $sth->fetchrow_hashref) {
		if($row->{'user_id'} != $l_user_id) {
			&PrintErrorExit($ls_uname_taken{$language});
		}
	}

	# See if this email address is already in use
	$email_lower = lc($email);
	$sth = &ExecSQL(
		"SELECT user_id " .
		"FROM users " .
		"WHERE LOWER(email)='$email_lower'"
		);

	while($row = $sth->fetchrow_hashref) {
		if($row->{'user_id'} != $l_user_id) {
			&PrintErrorExit($ls_email_already_in_use{$language});
		}
	}

	# Fix URL as the URL field is "http://" by default
	if($url eq "http://") {
		$url = "";
	}

	# Set status if not master admin account
	if(param('account_active') || $l_user_id == 1) {
		$status = $user_status_normal;
	} else {
		$status = $user_status_suspended;
	}

	# Set email privacy flag
	if(param('email_private')) {
		$email_private = 1;
	} else {
		$email_private = "NULL";
	}

	# Save base info
	$sth = &ExecSQL(
		"UPDATE users " .
		"SET " .
			"user_name='$l_user_name', " .
			"user_name_lower='$user_name_lower', " .
			"password='$password', " .
			"email='$email', " .
			"url='$url', " .
			"status=$status, " .
			"email_private=$email_private " .
		"WHERE user_id=$l_user_id"
		);

	# Handle permissions if not master admin account - it would
	# be bad to allow the admin account to revoke admin privs
	if($l_user_id != 1) {
		# Delete all existing permissions
		$sth = &ExecSQL(
			"DELETE FROM user_access_grants " .
			"WHERE user_id=$l_user_id"
			);

		# Give back whatever we got
		@permissions = param('permissions');
		foreach $permission (@permissions) {
			$sth = &ExecSQL(
				"INSERT INTO user_access_grants " .
				"(user_id, permission_id, granter_user_id, grant_utime) " .
				"VALUES ($l_user_id, $permission, $user_id, '$now_utime')"
				);
		}
	}

	# Do output template
	$output = &GetTemplate("user_saved_success.html");
	$output =~ s/REP_USER_ID/$l_user_id/g;
	$output =~ s/REP_USER_NAME/$l_user_name/g;

	&PrintSuccessExit($output);
}


#####################################################################
# GetLoginHistoryHTML($user_id)
#
# Returns the user $user_id's login history as HTML.
#####################################################################
sub GetLoginHistoryHTML() {
	my($l_user_id) = @_;
	my($row, $output, $entry_template, $all_entries, $entry_num, $this_entry,
		$timestamp, $ip, $hostname);

	$entry_template = &GetTemplate("user_login_history_field.html");

	$sth = &ExecSQL(
		"SELECT ip, hostname, login_utime " .
		"FROM login_log " .
		"WHERE user_id=$l_user_id " .
		"ORDER BY login_utime DESC"
		);

	$entry_num = $sth->rows;

	while($row = $sth->fetchrow_hashref) {
		$this_entry = $entry_template;
		$timestamp  = &UnixTimeToString($row->{'login_utime'});

		$this_entry =~ s/REP_LOGIN_NUMBER/$entry_num/g;
		$this_entry =~ s/REP_TIMESTAMP/$timestamp/g;
		$this_entry =~ s/REP_IP/$row->{'ip'}/g;
		$this_entry =~ s/REP_HOSTNAME/$row->{'hostname'}/g;

		# Alternate row background
		if($entry_num-- % 2 == 0) {
			$this_entry =~ s/REP_BGCOLOR/AAAAAA/g;
		} else {
			$this_entry =~ s/REP_BGCOLOR/CCCCCC/g;
		}

		$all_entries .= $this_entry;
	}

	$output = &GetTemplate("user_login_history.html");
	$output =~ s/REP_LOG_ENTRIES/$all_entries/g;

	return($output);
}

# END user_editor.cgi
