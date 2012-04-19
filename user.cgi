#!/usr/bin/perl

###########################################################################
# File      : user.cgi
# Purpose   : Non-admin user stuff: login/out, registration, password
#             reminder, preferences.
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

use Socket;
require "librecipants.pl";

# _____ GLOBAL VARIABLES ____________________________________________

$cmd = param('cmd');

# _____ END GLOBAL VARIABLES ________________________________________


&InitUser();	# Set up user info

# Check for a valid command
if(! $cmd || (
	$cmd ne "show_login" 		&& $cmd ne "logout"      	&&
	$cmd ne "show_new"   		&& $cmd ne "save_new"		&&
	$cmd ne "show_send_passwd"	&& $cmd ne "send_passwd"	&&
	$cmd ne "show_edit_info"	&& $cmd ne "save_edit_info"	&&
	$cmd ne "show_edit_passwd"	&& $cmd ne "save_passwd"	&&
	$cmd ne "profile"			&& $cmd ne "logout"			&&
	$cmd ne "login"				&& $cmd ne "set_language"	&&
	$cmd ne "show_bookmarks"	&& $cmd ne "add_bookmark"	&&
	$cmd ne "delete_bookmark"
	))
{
	&PrintErrorExit($ls_no_valid_command{$language});
}


if($cmd eq "login") {
	&Login();
}
elsif($cmd eq "show_login") {
	&LoginScreen();
}
elsif($cmd eq "logout") {
	&Logout();
}
elsif($cmd eq "show_new") {
	&SignupScreen();
}
elsif($cmd eq "save_new") {
	&SaveNewUser();
}
elsif($cmd eq "show_edit_info") {
	&EditInfoScreen();
}
elsif($cmd eq "save_edit_info") {
	&SaveInfo();
}
elsif($cmd eq "show_edit_passwd") {
	&EditPasswordScreen();
}
elsif($cmd eq "save_passwd") {
	&SavePassword();
}
elsif($cmd eq "show_send_passwd") {
	&SendPasswordScreen();
}
elsif($cmd eq "send_passwd") {
	&SendPassword();
}
elsif($cmd eq "save_new") {
	&SaveUser();
}
elsif($cmd eq "profile") {
	unless(param('user_id')) {
		&PrintErrorExit($ls_no_user_id{$language});
	}
	&ShowUserProfile(param('user_id'));
}
elsif($cmd eq "set_language") {
	&SetLanguage();
}
elsif($cmd eq "show_bookmarks") {
	&RecipeBookmarkScreen();
}
elsif($cmd eq "add_bookmark") {
	&AddRecipeBookmark();
}
elsif($cmd eq "delete_bookmark") {
	&DeleteRecipeBookmark();
}

&CleanExit(0);


# _____ FUNCTIONS  __________________________________________________

#####################################################################
# Login()
#
# If credentials match, sends a cookie containing the user's info.
#####################################################################
sub Login() {
	my($row, $user_name_lower, $password, $user_cookie, %cookie_vals,
		$signed_cookie_vals, $output);
	$user_name_lower = &DBEscapeString(lc(trim(param('user_name'))));
	$password        = trim(param('password'));

	# Bail if the user is already logged in
	if($logged_in) {
		&PrintErrorExit($ls_already_signed_in_as{$language} . " $user_name!");
	}

	# Check for required args
	if($user_name_lower eq "" || $password eq "") {
		&LoginScreen($ls_need_uname_and_passwd{$language});
		&CleanExit(0);
	}

	# Retrieve user's info and attempt to authenticate
	$sth = &ExecSQL(
		"SELECT user_id, user_name, password, status " .
		"FROM users " .
		"WHERE user_name_lower='$user_name_lower'");

	if($row = $sth->fetchrow_hashref) {
		# Check password
		if($password ne $row->{'password'}) {
			&LoginScreen($ls_login_auth_failed{$language});
			&CleanExit(0);
		}

		# Check status
		if($row->{'status'} != $user_status_normal) {
			&PrintErrorExit($ls_account_inactive{$language});
		}
	
		$cookie_vals{'user_name'} = $row->{'user_name'};
		$cookie_vals{'user_id'}   = $row->{'user_id'};
	} else {
		&LoginScreen($ls_login_auth_failed{$language});
		&CleanExit(0);
	}

	# Encode and sign hash for cookie
	$signed_cookie_vals = &CookieEncodeSign(%cookie_vals);

	$user_cookie = cookie(
		-name   => 'rp_user',
		-value  => $signed_cookie_vals,
		-domain => $cookie_domain,
		-path   => $cookie_path
		);

	# Set user info as InitUser() won't do any good here
	$logged_in = 1;
	$user_name = $cookie_vals{'user_name'};
	$user_id   = $cookie_vals{'user_id'};

	&LogLogin();

	$output = &GetTemplate("success_box.html");
	$output =~ s/REP_MESSAGE/$row->{'user_name'} signed in!/g;

	&ShowPage($row->{'user_name'} . " " . $ls_signed_in{$language},
		$output, $user_cookie);
}


#####################################################################
# Logout()
#
# Logs a user out by deleting the "user" cookie (setting the same
# cookie with an expiration date in the past.
#####################################################################
sub Logout() {
	my($output, $logout_cookie, $user_cookie_vals);

	if(! $logged_in) {
		&PrintErrorExit($ls_cant_log_out_not_logged_in{$language});
	}

	$user_cookie_vals = cookie('rp_user');

	$logout_cookie = cookie(
		-name    => 'rp_user',
		-value   => $user_cookie_vals,
		-domain  => $cookie_domain,
		-path    => $cookie_path,
		-expires => '-5y'
		);

	# Set user info as InitUser() won't do any good here
	$logged_in = 0;
	$user_name = "";
	$user_id   = "";

	$output = &GetTemplate("success_box.html");
	$output =~ s/REP_MESSAGE/$user_name $ls_signed_out{$language}/g;

	&ShowPage("$user_name " . $ls_signed_out{$language},
		$output, $logout_cookie);
}


#####################################################################
# LoginScreen()
#
# Displays the login screen, with optional error message $message.
#####################################################################
sub LoginScreen() {
	my($message) = @_;
	my($output, $error_box);

	# Bail if the user is already logged in
	if($logged_in) {
		&PrintErrorExit($ls_already_logged_in_as{$language} . "$user_name!");
	}

	$output = &GetTemplate("user_login_form.html");

	if($message) {
		$error_box = &GetTemplate("error_box.html");
		$error_box =~ s/REP_MESSAGE/$message/g;
		$output = $error_box . $output;
	}
		
	&ShowPage($ls_sign_in_title{$language}, $output);
}


#####################################################################
# SignupScreen($user_name, $email, $url, $message)
#
# Displays the login screen, with optional error message $message.
#####################################################################
sub SignupScreen() {
	my($l_user_name, $email, $email_private, $url, $message) = @_;
	my($output, $error_box);

	# Bail if the user is already logged in
	if($logged_in) {
		&PrintErrorExit($ls_already_logged_in_as{$language} . "$user_name!");
	}

	$output = &GetTemplate("user_signup_form.html");

	# Get the error template and fill it out if we got an error message
	if($message) {
		$error_box = &GetTemplate("error_box.html");
		$error_box =~ s/REP_MESSAGE/$message/g;
		$output = $error_box . $output;
	}

	# If we don't have a URL, set it to 'http://'
	if($url eq "") {
		$url = "http://";
	}

	if($email_private) {
		$output =~ s/NAME=\"email_private\"/NAME=\"email_private\" CHECKED/g;
	}
	$output =~ s/REP_USER_NAME/$l_user_name/g;
	$output =~ s/REP_EMAIL/$email/g;
	$output =~ s/REP_URL/$url/g;		
	&ShowPage("Sign Up for ReciPants!", $output);
}


#####################################################################
# SaveNewUser()
#
# The name pretty much says it all.
#####################################################################
sub SaveNewUser() {
	my($user_name, $user_name_lower, $password, $email, $email_lower, 
		$url, $user_id, $email_private, $row);

	# Bail if the user is already logged in
	if($logged_in) {
		&PrintErrorExit($ls_already_logged_in_as{$language} . "$user_name!");
	}

	$user_name       = &DBEscapeString(trim(param('user_name')));
	$user_name_lower = lc($user_name);
	$email           = &DBEscapeString(trim(param('email')));
	$url             = &DBEscapeString(trim(param('url')));		# not required
	if(param('email_private') eq "on") {
		$email_private = 1;
	} else {
		$email_private = 0;
	}

	# Check for required args
	if($user_name eq "" || $email eq "") {
		&SignupScreen($user_name, $email, $email_private, $url, $ls_missing_uname_and_email{$language});
		&CleanExit(0);
	}

	# Validate email address length
	if(length($email) > 75) {
		&SignupScreen($user_name, $email, $email_private, $url, $ls_email_too_long{$language});
		&CleanExit(0);
	}

	# Validate email address format
	unless(&EmailOK($email)) {
		&SignupScreen($user_name, $email, $email_private, $url, $ls_bad_email_format{$language});
		&CleanExit(0);
	}

	# Validate user name length
	if(length($user_name) > 30) {
		&SignupScreen($user_name, $email, $email_private, $url, $ls_uname_too_long{$language});
		&CleanExit(0);
	}

	# See if this username is taken
	$sth = &ExecSQL(
		"SELECT 1 " .
		"FROM users " .
		"WHERE user_name_lower='$user_name_lower'"
		);

	if($row = $sth->fetchrow_hashref) {
		&SignupScreen($user_name, $email, $email_private, $url, $ls_uname_taken{$language});
		&CleanExit(0);
	}

	# See if this email address is already in use
	$email_lower = lc($email);
	$sth = &ExecSQL(
		"SELECT 1 " .
		"FROM users " .
		"WHERE LOWER(email)='$email_lower'"
		);

	if($row = $sth->fetchrow_hashref) {
		&SignupScreen($user_name, $email, $email_private, $url,
			$ls_email_already_in_use{$language});
		&CleanExit(0);
	}

	# Fix URL as the URL field is "http://" by default
	if($url eq "http://") {
		$url = "";
	}

	# Generate temporary password
	$password = int(rand(99999999));

	&InsertUser($user_name, $password, $email, $email_private, $url, $user_status_normal);

	# Fill out and send welcome email with account info
	$email_output = &GetTemplate("welcome_email.txt");
	$email_output =~ s/REP_INSTALLED_URL/$app_installed_url/g;
	$email_output =~ s/REP_USER_NAME/$user_name/g;
	$email_output =~ s/REP_PASSWORD/$password/g;
	$email_output =~ s/REP_APP_HOST_TITLE/$app_host_title/g;
	$email_output =~ s/REP_APP_HOST_URL/$app_host_url/g;
	$email_output =~ s/REP_APP_VERSION/$app_version/g;
	$email_output =~ s/REP_APP_URL/$app_url/g;

	&SendEmail("ReciPants at $app_host_title", $system_email_from_address,
		$user_name, $email, $ls_welcome_email_subject{$language}, $email_output);

	&PrintSuccessExit($ls_create_account_success{$language});
}


#####################################################################
# InsertUser()
#
# Inserts a user record and returns the new user_id.
#####################################################################
sub InsertUser() {
	my($user_name, $password, $email, $email_private, $url, $status) = @_;
	my($user_name_lower, $oid, $user_id, $row, $now_utime);

	$user_name_lower = lc($user_name);
	$now_utime       = time();

	$sth = &ExecSQL(
		"INSERT INTO users " .
			"(user_name, user_name_lower, password, email, email_private, " .
			"url, status, create_utime) " .
		"VALUES " .
			"('$user_name', '$user_name_lower', '$password', '$email', " .
			"$email_private, '$url', $status, '$now_utime')"
		);


	# Get the newly created user_id which is generated by a 
	# sequence in the database. Database-dependant.

	# Postgres
	if($db_driver eq "Pg") {
		$oid = $sth->{pg_oid_status};

		$sth = &ExecSQL(
		 	"SELECT user_id " .
			"FROM users " .
			"WHERE oid=$oid"
			);

		if($row = $sth->fetchrow_hashref) {
			$new_user_id = $row->{'user_id'};
		}
	}

	# MySQL
	elsif($db_driver eq "mysql") {
		$new_user_id = $sth->{mysql_insertid};
	}

	# Did we get the new user id?
	if($new_user_id) {
		return($new_user_id);
	} else {
		&PrintErrorExit("InsertUser(): " . $ls_cant_get_new_user_id{$language});
	}
}


#####################################################################
# EditPasswordScreen()
#
# Displays the change password screen, with optional error message $message.
#####################################################################
sub EditPasswordScreen() {
	my($message) = @_;
	my($output, $error_box);

	# Bail if the user isn't logged in
	unless($logged_in) {
		&PrintErrorExit($ls_must_be_signed_in{$language});
	}

	$output = &GetTemplate("user_change_password_form.html");

	# Get the error template and fill it out if we got an error message
	if($message) {
		$error_box = &GetTemplate("error_box.html");
		$error_box =~ s/REP_MESSAGE/$message/g;
		$output = $error_box . $output;
	}

	&ShowPage($ls_change_passwd_title{$language}, $output);
}


#####################################################################
# SavePassword()
#
# Saves a user's password.
#####################################################################
sub SavePassword() {
	my($current_password, $old_password, $new_password_1, $old_password_2);

	# Bail if the user isn't logged in
	unless($logged_in) {
		&PrintErrorExit($ls_must_be_signed_in{$language});
	}

	$old_password   = trim(param('old_password'));
	$new_password_1 = trim(param('new_password_1'));
	$new_password_2 = trim(param('new_password_2'));

	# Check for required args
	if($old_password eq "" || $new_password_1 eq "" || $new_password_2 eq "") {
		&EditPasswordScreen($ls_fill_in_all_fields{$language});
		&CleanExit(0);
	}

	# Make sure both new passwords are the same
	if($new_password_1 ne $new_password_2) {
		&EditPasswordScreen($ls_new_passwds_dont_match{$language});
		&CleanExit(0);
	}

	# Verify length
	if(length($new_password_1) < 6 || length($new_password_1) > 20) {
		&EditPasswordScreen($ls_bad_passwd_length{$language});
		&CleanExit(0);
	}

	# Verify current password
	$current_password = &GetUserPassword($user_id);

	if($old_password ne $current_password) {
		&EditPasswordScreen($ls_bad_current_passwd{$language});
		&CleanExit(0);
	}

	&UpdateUserPassword($user_id, $new_password_1);
	&PrintSuccessExit($ls_passwd_change_success{$language});
}


#####################################################################
# GetUserPassword($user_id)
#
# Returns the password for user $user_id.
#####################################################################
sub GetUserPassword() {
	my($l_user_id) = @_;
	my($row);

	$sth = &ExecSQL(
		"SELECT password " .
		"FROM users " .
		"WHERE user_id=$l_user_id"
		);

	if($row = $sth->fetchrow_hashref) {
		return($row->{'password'});
	} else {
		return("");
	}
}


#####################################################################
# UpdateUserPassword($user_id, $new_password)
#
# Returns the password for user $user_id.
#####################################################################
sub UpdateUserPassword() {
	my($l_user_id, $new_password) = @_;

	$new_password = &DBEscapeString($new_password);

	$sth = &ExecSQL(
		"UPDATE users " .
		"SET password='$new_password' " .
		"WHERE user_id=$l_user_id"
		);
}


#####################################################################
# SendPassword()
#
# Sends an email to the user with their login info.
#####################################################################
sub SendPassword() {
	my($user_name, $password, $email, $row);
	$email = trim(param('email'));

	# Bail if the user is already logged in
	if($logged_in) {
		&PrintErrorExit($ls_already_signed_in_as{$language} . "$user_name!");
	}

	# Check for required arg
	if($email eq "") {
		&SendPasswordScreen($ls_missing_emai{$language});
		&CleanExit(0);
	}

	# Get user info
	$sth = &ExecSQL(
		"SELECT user_name, password " .
		"FROM users " .
		"WHERE email='$email'"
		);

	unless($row = $sth->fetchrow_hashref) {
		&SendPasswordScreen($ls_no_account_match_for_email{$language});
		&CleanExit(0);
	}

	# Fill out and send reminder email with account info
	$email_output = &GetTemplate("user_password_reminder_email.txt");
	$email_output =~ s/REP_INSTALLED_URL/$app_installed_url/g;
	$email_output =~ s/REP_USER_NAME/$row->{'user_name'}/g;
	$email_output =~ s/REP_PASSWORD/$row->{'password'}/g;
	$email_output =~ s/REP_APP_HOST_TITLE/$app_host_title/g;
	$email_output =~ s/REP_APP_HOST_URL/$app_host_url/g;
	$email_output =~ s/REP_APP_VERSION/$app_version/g;
	$email_output =~ s/REP_APP_URL/$app_url/g;

	&SendEmail("ReciPants at $app_host_title", $system_email_from_address,
		$user_name, $email, $ls_passwd_reminder_email_subject{$language},
		$email_output);

	&PrintSuccessExit($ls_passwd_reminder_success{$language});
}


#####################################################################
# SendPasswordScreen()
#
# Displays the remind password screen, with optional error message $message.
#####################################################################
sub SendPasswordScreen() {
	my($message) = @_;
	my($output, $error_box);

	# Bail if the user is already logged in
	if($logged_in) {
		&PrintErrorExit($ls_already_signed_in_as{$language} . "$user_name!");
	}

	$output = &GetTemplate("user_send_password_form.html");

	# Get the error template and fill it out if we got an error message
	if($message) {
		$error_box = &GetTemplate("error_box.html");
		$error_box =~ s/REP_MESSAGE/$message/g;
		$output = $error_box . $output;
	}

	&ShowPage($ls_send_passwd_title{$language}, $output);
}


#####################################################################
# ShowUserProfile($user_id)
#
# Displays the remind password screen, with optional error message $message.
#####################################################################
sub ShowUserProfile() {
	my($l_user_id) = @_;
	my($user_info, $row, $output, $user_name, $email, $url, $recipe_count,
		$users_recipe_list, $users_recipe_output);

	$output = &GetTemplate("user_profile.html");

	if($user_info = &GetUserInfo($l_user_id)) {
		$user_name = $user_info->{'user_name'};
		$url       = $user_info->{'url'};
	}

	# Handle email privacy flag
	if($user_info->{'email_private'}) {
		$email = $ls_email_private{$language};
	} else {
		$email = "<A HREF=\"mailto:" . $user_info->{'email'} . "\">" .
			$user_info->{'email'} . "</A>";
	}

	# Handle URL
	if($url eq "") {
		$url = "&lt;" . $ls_none{$language} . "&gt;";
	} else {
		$url = "<A HREF=\"$url\" TARGET=\"_blank\">$url</A>";
	}

	# Do count of submitted recipes
	$sth = &ExecSQL(
		"SELECT COUNT(author_user_id) AS recipe_count " .
		"FROM recipes " .
		"WHERE author_user_id=$l_user_id"
		);

	if($row = $sth->fetchrow_hashref) {
		$recipe_count = $row->{'recipe_count'};
	} else {	# Shouldn't be necessary, but BSTS
		$recipe_count = 0;
	}

	# Get list of recipes by this user
	$users_recipe_list = &GetRecipesEnteredByUserHTML($l_user_id);
	if($users_recipe_list ne "") {
		$users_recipe_output = &GetTemplate("user_profile_user_recipes.html");
		$users_recipe_output =~ s/REP_USER_NAME/$user_name/g;
		$users_recipe_output =~ s/REP_RECIPES/$users_recipe_list/g;
	}

	$output =~ s/REP_URL/$url/g;
	$output =~ s/REP_EMAIL/$email/g;
	$output =~ s/REP_RECIPE_COUNT/$recipe_count/g;
	$output =~ s/REP_RECIPE_LIST/$users_recipe_output/g;

	&ShowPage($ls_profile_for{$language} . $user_name, $output);
}


#####################################################################
# SetLanguage()
#
# Logs a user out by deleting the "user" cookie (setting the same
# cookie with an expiration date in the past.
#####################################################################
sub SetLanguage() {
	my($l_language, $old_language_cookie, $new_language_cookie, 
		$new_language, $language_found);

	# Check for arg
	$l_language = lc(&trim(param('language')));

	unless($l_language) {
		&PrintErrorExit($ls_missing_language_code{$language});
	}

	# Make a cookie with the current language to expire
	$old_language_cookie = cookie(
		-name    => 'rp_language',
		-value   => $language,
		-domain  => $cookie_domain,
		-path    => $cookie_path,
		-expires => '-5y'
		);

	# Make sure we support the language. If so, set the $language global
	# so the success page prints in the newly selected language.
	foreach $supported_language (@supported_languages) {
		if($supported_language eq $l_language) {
			$language       = $l_language;
			$language_found = 1;
			last;
		}
	}

	# Make the new cookie
	$new_language_cookie = cookie(
		-name    => 'rp_language',
		-value   => $language,
		-domain  => $cookie_domain,
		-path    => $cookie_path,
		-expires => '+1y'
		);

	# If we support the language, try to redirect to the page the user changed 
	# the language from. If we don't support the language, print an error.
	if($language_found) {

		if(referer() ne "") {
			# Don't use the CGI redirect() method or you can't set cookies.
			print header(
				-cookie   => [$old_language_cookie, $new_language_cookie],
				-Location => referer()
				);
		} else {
			$output = &GetTemplate("success_box.html");
			$output =~ s/REP_MESSAGE/Language saved/g;

			&ShowPage($ls_language_set_success_title{$language}, $output,
				[$old_language_cookie, $new_language_cookie]);
		}
	} else {
		$output = &GetTemplate("error_box.html");
		$output =~ s/REP_MESSAGE/$ls_language_not_found{$language}/g;

		&ShowPage($ls_language_not_found{$language}, $output);
	}
}


#####################################################################
# EditInfoScreen($message)
#
# Shows an edit info form with optional error message $message.
#####################################################################
sub EditInfoScreen() {
	my($message) = @_;
	my($output, $error_box, $user_base_info);

	# Bail if the user isn't logged in
	unless($logged_in) {
		&PrintErrorExit($ls_must_be_signed_in{$language});
	}

	# Get user info
	unless($user_base_info = &GetUserInfo($user_id)) {
		&PrintErrorExit($ls_user_not_found{$language});
	}

	# Get the error template and fill it out if we got an error message
	if($message) {
		$output = &GetTemplate("error_box.html");
		$output =~ s/REP_MESSAGE/$message/g;
	}

	$output .= &GetTemplate("user_change_info_form.html");

	if($user_base_info->{'email_private'} == 1) {
		$output =~ s/(NAME=\"email_private\")/$1 CHECKED/g;
	}
	$output =~ s/REP_EMAIL/$user_base_info->{'email'}/g;
	$output =~ s/REP_URL/$user_base_info->{'url'}/g;

	&ShowPage($ls_change_info_title{$language}, $output);
}


#####################################################################
# SaveInfo()
#
# The name pretty much says it all.
#####################################################################
sub SaveInfo() {
	my($email, $email_lower, $url, $email_private, $row);

	# Bail if the user isn't logged in
	unless($logged_in) {
		&PrintErrorExit($ls_must_be_signed_in{$language});
	}

	$email = &DBEscapeString(trim(param('email')));
	$url   = &DBEscapeString(trim(param('url')));		# not required
	if(param('email_private') eq "on") {
		$email_private = 1;
	} else {
		$email_private = 0;
	}

	# Check for required args
	if($user_name eq "" || $email eq "") {
		&EditInfoScreen($ls_missing_uname_and_email{$language});
		&CleanExit(0);
	}

	# Validate email address length
	if(length($email) > 75) {
		&EditInfoScreen($ls_email_too_long{$language});
		&CleanExit(0);
	}

	# Validate email address format
	unless(&EmailOK($email)) {
		&EditInfoScreen($ls_bad_email_format{$language});
		&CleanExit(0);
	}

	# See if this email address is already in use
	$email_lower = lc($email);
	$sth = &ExecSQL(
		"SELECT user_id " .
		"FROM users " .
		"WHERE user_id != $user_id AND LOWER(email)='$email_lower'"
		);

	if($row = $sth->fetchrow_hashref) {
		if($row->{'user_id'} == $user_id) {
			&EditInfoScreen($ls_email_already_in_use{$language});
			&CleanExit(0);
		}
	}

	# Fix URL as the URL field is "http://" by default
	if($url eq "http://") {
		$url = "";
	}

	# Save it
	$dbh = &ExecSQL(
		"UPDATE users " .
		"SET " .
			"email='$email', " .
			"email_private=$email_private, " .
			"url='$url' " .
		"WHERE user_id=$user_id"
		);

	&PrintSuccessExit($ls_save_info_success{$language});
}


#####################################################################
# AddRecipeBookmark()
#
# Inserts a bookmark for recipe param(recipe_id) for current user.
#####################################################################
sub AddRecipeBookmark() {
	my($recipe_id);

	# Bail if the user isn't logged in
	unless($logged_in) {
		&PrintErrorExit($ls_must_be_signed_in{$language});
	}

	# Bail if no recipe id
	$recipe_id = param('recipe_id');
	unless($recipe_id) {
		&PrintErrorExit($ls_no_recipe_id{$language});
	}

	$sth = &ExecSQL(
		"INSERT INTO user_recipe_bookmarks " .
			"(user_id, recipe_id) " .
		"VALUES " .
			"($user_id, $recipe_id)"
		);

	&RecipeBookmarkScreen($ls_add_recipe_bookmark_success{$language});
}


#####################################################################
# DeleteRecipeBookmark()
#
# Deletes a bookmark for recipe param(recipe_id) for current user.
#####################################################################
sub DeleteRecipeBookmark() {
	my($recipe_id);

	# Bail if the user isn't logged in
	unless($logged_in) {
		&PrintErrorExit($ls_must_be_signed_in{$language});
	}

	# Bail if no recipe id
	$recipe_id = param('recipe_id');
	unless($recipe_id) {
		&PrintErrorExit($ls_no_recipe_id{$language});
	}

	$sth = &ExecSQL(
		"DELETE FROM user_recipe_bookmarks " .
		"WHERE user_id=$user_id " .
			"AND recipe_id=$recipe_id"
		);

	&RecipeBookmarkScreen($ls_delete_recipe_bookmark_success{$language});
}


#####################################################################
# RecipeBookmarkScreen($message)
#
# Displays the Bookmark Manager screen with optional success message 
# $message.
#####################################################################
sub RecipeBookmarkScreen() {
	my($message) = @_;
	my($output, $message_box, $bookmarks);

	# Bail if the user isn't logged in
	unless($logged_in) {
		&PrintErrorExit($ls_must_be_signed_in{$language});
	}

	$output = &GetTemplate("recipe_bookmarks_edit.html");

	# Get message template and fill it out
	if($message) {
		$message_box = &GetTemplate("success_box.html");
		$message_box =~ s/REP_MESSAGE/$message/g;
		$output      = $message_box . $output;
	}

	$bookmarks = &GetRecipeBookmarksHTML($user_id);
	$output =~ s/REP_BOOKMARKS/$bookmarks/g;

	&ShowPage($ls_recipe_bookmarks_title{$language}, $output);
}


#####################################################################
# GetRecipeBookmarks($user_id)
#
# Returns an array of hashrefs to recipe info for recipes that are in
# user $user_id's recipe bookmarks list.
#####################################################################
sub GetRecipeBookmarks() {
	my($l_user_id) = @_;
	my($row);

	$sth = &ExecSQL(
		"SELECT urb.recipe_id, r.name " .
		"FROM user_recipe_bookmarks urb, recipes r " .
		"WHERE urb.user_id=$user_id " .
			"AND r.recipe_id=urb.recipe_id " .
		"ORDER BY r.name"
		);

	while($row = $sth->fetchrow_hashref) {
		push(@bookmarks, $row);
	}

	if($#bookmarks < 0) {
		@bookmarks = ();
	}

	return(@bookmarks);
}


#####################################################################
# GetRecipeBookmarksHTML($user_id)
#
# Returns an array of hashrefs to recipe info for recipes that are in
# user $user_id's recipe bookmarks list.
#####################################################################
sub GetRecipeBookmarksHTML() {
	my($l_user_id) = @_;
	my(@bookmarks, $bookmark, $bookmark_template, $this_bookmark,
		$bookmarks_output, $output);

	@bookmarks = &GetRecipeBookmarks($l_user_id);

	if($#bookmarks >= 0) {
		$bookmark_template = &GetTemplate("recipe_bookmark.html");

		foreach $bookmark (@bookmarks) {
			$this_bookmark =  $bookmark_template;
			$this_bookmark =~ s/REP_RECIPE_ID/$bookmark->{'recipe_id'}/g;
			$this_bookmark =~ s/REP_NAME/$bookmark->{'name'}/g;
			$output       .= $this_bookmark;
		}
	} else {
		$output = &GetTemplate("recipe_bookmarks_none.html");
	}

	return($output);
}


#####################################################################
# LogLogin()
#
# Logs a user login to the LOGIN_LOG table.
#####################################################################
sub LogLogin() {
	my($ip, $hostname, $now_utime);

	$ip         = $ENV{REMOTE_ADDR};
	($hostname) = gethostbyaddr(inet_aton($ip), AF_INET);
	$now_utime  = time();

	$sth = &ExecSQL(
		"INSERT INTO login_log (user_id, ip, hostname, login_utime) " .
		"VALUES ($user_id, '$ip', '$hostname', '$now_utime')"
	);
}

# END user.cgi
