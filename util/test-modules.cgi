#!/usr/bin/perl

###########################################################################
# File      : test-modules.cgi
# Purpose   : Diagnostic - tests for required Perl modules.
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

use strict;

# _____ GLOBAL VARIABLES ____________________________________________

my(@required_modules, @database_modules, @optional_modules, $module);

# _____ END GLOBAL VARIABLES ________________________________________


# Print MIME header
print "Content-type: text/html\r\n\r\n";


# Module info
@required_modules = (
	{
		name 		=> "CGI",
		description => "Provides basic CGI functionality. Comes with Perl.",
		url			=> "http://search.cpan.org/~lds/CGI.pm-3.00/CGI.pm",
		},
	{
		name		=> "CGI::Cookie",
		description => "Provides acccess to HTTP cookies.",
		url			=> "http://search.cpan.org/~lds/CGI.pm-3.00/CGI/Cookie.pm",
		},
	{
		name		=> "Math::Fraction",
		description => "Converts between fractions and decimals. Required for measurement conversion.",
		url			=> "http://search.cpan.org/author/KEVINA/Fraction-v.53b/Fraction.pm",
		},
	{
		name		=> "Digest::SHA1",
		description => "SHA-1 hashing algorith. Required for tamper-proof user cookies.",
		url			=> "http://search.cpan.org/author/GAAS/Digest-SHA1-2.04/SHA1.pm",
		},
	{
		name		=> "DBI",
		description => "Generic database interface system. Required to talk to databases.",
		url			=> "http://search.cpan.org/author/TIMB/DBI-1.38/DBI.pm",
		}
);

@database_modules = (
	{
		name		=> "DBD::Pg",
		description => "Driver for Postgres databases. Only required if you use Postgres as your database.",
		url			=> "http://search.cpan.org/author/MERGL/pgsql_perl5-1.9.0/Pg.pm",
		},

	{
		name		=> "DBD::mysql",
		description => "Driver for MySQL databases. Only required if you use MySQL as your database.",
		url			=> "http://search.cpan.org/author/RUDY/DBD-mysql-2.9002/",
		},

	{
		name		=> "DBD::Oracle",
		description => "Driver for Oracle databases. Only required if you use Oracle as your database.",
		url			=> "http://search.cpan.org/author/TIMB/DBD-Oracle-1.15/",
		}
);

@optional_modules = (
	{
		name		=> "Net::SMTP",
		description => "Allows sending of email using an SMTP server. Not required if you use a local installation of sendmail instead.",
		url			=> "http://search.cpan.org/author/MERGL/pgsql_perl5-1.9.0/Pg.pm",
		}
);


# Print set-up HTML. This is deliberately not templated to avoid confusion.
print <<EOD;
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/1999/REC-html401-19991224/loose.dtd">
<HTML>
<HEAD>
	<TITLE>ReciPants Perl Module Test</TITLE>
	<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=iso-8859-1">
	<META HTTP-EQUIV="Content-Language" CONTENT="en">
	<META NAME="Robots" CONTENT="none">
	<META NAME="MSSmartTagsPreventParsing" CONTENT="TRUE">
	<LINK REL="stylesheet" HREF="../static/css/recipe.css" TYPE="text/css" MEDIA="screen">
	<LINK REL="SHORTCUT ICON" HREF="../favicon.ico">
</HEAD>
<BODY BGCOLOR="#FFFFFF" LINK="#FF0000" ALINK="#FF0000" VLINK="#FF0000">

<FONT FACE="Arial,Helvetica,sans-serif">

<H1>ReciPants Perl Module Test</H1>

<TABLE BORDER="0" WIDTH="450">
<TR>
	<TD>
		<SPAN CLASS="text">
		<B>This program tests to see if you have the Perl modules required 
		to run ReciPants.</B>
		<BR><BR>
		<P>
		Looking for modules in (<CODE>\@INC</CODE> = ):
		<P>
EOD


print "<CODE>\n", join("<BR>\n", @INC), "\n</CODE>\n\n";
print <<EOD;
		<BR><BR>

		<B>
		Modules in <FONT COLOR="#009933"><B>green</B></FONT> are installed and presumed OK;
		modules in <FONT COLOR="#FF0000"><B>red</B></FONT> could not be found on your system.
		</B>

		<BR><BR>
EOD


# Processs modules:
# Required modules
print "<H2>Required Modules</H2>\n";
print "<H3>You must have all of these modules installed to run ReciPants.</H3>\n\n";

foreach $module (@required_modules) {
	&PrintModuleInfo($module);
}


# DB modules
print "<H2>Database Modules</H2>\n";
print "<H3>You must have the proper module for your database installed.</H3>\n\n";

foreach $module (@database_modules) {
	&PrintModuleInfo($module);
}


# Optional modules
print "<H2>Optional Modules</H2>\n";
print "<H3>These modules are not necessary if you fullfill the alternate requirements.</H3>\n\n";

foreach $module (@optional_modules) {
	&PrintModuleInfo($module);
}


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



# _____ FUNCTIONS  __________________________________________________

#####################################################################
# PrintModuleInfo($module)
#
# Takes a hashref of module info, sees if it's installed, and prints
# the results and module info.
#####################################################################
sub PrintModuleInfo() {
	my($module) = @_;

	# Try to "use" the module
	eval("use " . $module->{name} . ";");

	# See if that produced any errors
	if($@) {
		print
			"<SPAN CLASS=\"subhead\"><FONT COLOR=\"#FF0000\"><B>", $module->{name},
			"</B> not found</FONT></SPAN> - [<A HREF=\"", $module->{url},
			"\" TARGET=\"_blank\">download</A>]";
	} else {
		print
			"<FONT COLOR=\"#009933\"><B>", $module->{name}, "</B> v",
			$module->{name}->VERSION, " found</FONT>";
	}

	print "<BR>\n", $module->{description}, "<BR><BR>\n\n";
}

# END test-modules.cgi
