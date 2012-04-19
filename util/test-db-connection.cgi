#!/usr/bin/perl -w

###########################################################################
# File      : test-db-connection.cgi
# Purpose   : Diagnostic - tests for database connection.
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

use DBI;
require "../recipants.cfg.pl";

# _____ GLOBAL VARIABLES ____________________________________________

my($dbh, $sth, $row);
	
# _____ END GLOBAL VARIABLES ________________________________________


# Print MIME header
print "Content-type: text/html\r\n\r\n";


# Print set-up HTML. This is deliberately not templated to avoid confusion.
print <<EOD;
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/1999/REC-html401-19991224/loose.dtd">
<HTML>
<HEAD>
	<TITLE>ReciPants Database Connection Test</TITLE>
	<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=iso-8859-1">
	<META HTTP-EQUIV="Content-Language" CONTENT="en">
	<META NAME="Robots" CONTENT="none">
	<META NAME="MSSmartTagsPreventParsing" CONTENT="TRUE">
	<LINK REL="stylesheet" HREF="../static/css/recipe.css" TYPE="text/css" MEDIA="screen">
	<LINK REL="SHORTCUT ICON" HREF="../favicon.ico">
</HEAD>
<BODY BGCOLOR="#FFFFFF" LINK="#FF0000" ALINK="#FF0000" VLINK="#FF0000">

<FONT FACE="Arial,Helvetica,sans-serif">

<H1>ReciPants Database Connection Test</H1>

<TABLE BORDER="0" WIDTH="450">
<TR>
	<TD>
		<SPAN CLASS="text">
		<B>This program tests to see if ReciPants can connect to your database
		with the settings specified in <CODE>recipants.cfg.pl</CODE>.</B>
		<P>
EOD

open(STDERR, ">&STDOUT");	# Redirect STDERR so errors go to the screen instead of Web server log

print "Using database driver &quot;$db_driver&quot;<BR><BR>\n";

# Connect to database
print "Connecting to database...<BR>\n";
if($dbh = DBI->connect (
	"dbi:$db_driver:dbname=$db_name",
	$db_uname,
	$db_passwd
	))
{
	print "<FONT COLOR=\"#009933\">Connected OK</FONT><BR><BR>\n";
} else {
	&Bail("<FONT COLOR=\"#FF0000\">ERROR: Can't connect to database: " . $DBI::errstr . "</FONT>");
}

# Prepare statement
print "Preparing SQL statement...<BR>\n";
if($sth = $dbh->prepare("SELECT 1 AS test")) {
	print "<FONT COLOR=\"#009933\">Statement prepared OK</FONT><BR><BR>\n";
} else {
	&Bail("<FONT COLOR=\"#FF0000\">ERROR: Can't prepare statement: " . $dbh->errstr() . "</FONT>");
}

# Execute statement
print "Executiing SQL statement...<BR>\n";
if($sth->execute()) {
	print "<FONT COLOR=\"#009933\">Statement executed OK</FONT><BR><BR>\n";
} else {
	&Bail("<FONT COLOR=\"#FF0000\">ERROR: Can't execute statement: " . $dbh->errstr() . "</FONT>");
}

# Fetch results
print "Fetching result...<BR>\n";
if($sth->fetchrow_hashref()) {
	print "<FONT COLOR=\"#009933\">Got result OK</FONT><BR><BR>\n";
} else {
	&Bail("<FONT COLOR=\"#FF0000\">ERROR: Can't fetch result: " . $dbh->errstr() . "</FONT>");
}


# Disconnect
print "Disconnecting from database...<BR>\n";
$sth->finish();
if($dbh->disconnect()) {
	print "<FONT COLOR=\"#009933\">Disconnected OK</FONT><BR><BR>\n";
} else {
	&Bail("<FONT COLOR=\"#FF0000\">ERROR: Can't disconnect from database: " . $DBI::errstr . "</FONT>");
}


&Bail("<FONT COLOR=\"#009933\">ReciPants can talk to your database!</FONT>");



# _____ FUNCTIONS  __________________________________________________

#####################################################################
# Bail($message)
#
# Prints message $message and ending HTML and exits the program.
#####################################################################
sub Bail() {
	my($message) = @_;

	print "<B>$message</B>\n\n";

	# Ending HTML
	print <<EOD;
		</SPAN>

	</TD>
</TR>
</TABLE>

</BODY>
</HTML>
EOD

	exit(0);
}

# END test-db-connnection.cgi
