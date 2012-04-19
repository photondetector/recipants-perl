#!/usr/bin/perl

###########################################################################
# File      : utility.cgi
# Purpose   : Displays user utilities. Essentially a wrapper for displaying
#             static util pages with the corrent menus and such.
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

$util = lc(param('util'));

# _____ END GLOBAL VARIABLES ________________________________________


&InitUser();	# Set up user info


# What are we doing?
if($util eq "temperature_converter") {
	&ShowTemperatureConverter();
} elsif($util eq "sweetness_converter") {
	&ShowSweetnessConverter();
} else {
	&PrintErrorExit($ls_no_valid_command{$language});
}
            
&CleanExit(0);


# _____ FUNCTIONS ___________________________________________________

#####################################################################
# ShowTemperatureConverter()
#
# Dumps the temerature (F <-> C) converter utility.
#####################################################################
sub ShowTemperatureConverter() {
	my($output);

	$output = &GetTemplate("util_temperature_converter.html");

	&ShowPage($ls_temperature_converter{$language}, $output);
}



#####################################################################
# ShowSweetnessConverter()
#
# Dumps the sweetness (Brix <-> Baume) converter utility.
#####################################################################
sub ShowSweetnessConverter() {
	my($output);

	$output = &GetTemplate("util_sweetness_converter.html");

	&ShowPage($ls_sweetness_converter{$language}, $output);
}


# END utility.cgi
