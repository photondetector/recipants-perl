#!/usr/bin/perl

###########################################################################
# File      : category.cgi
# Purpose   : Generates a random string to be used as the secret host key.
# Program   : ReciPants ( http://recipants.photondetector.com/ )
# Version   : 1.1.1
# Authors   : Authors of Scoop ( http://scoop.kuro5hin.org/ )
#             Nick Grossman <nick@photondetector.com>
# Tab stops : 4
#
# Copyright (c) 2002, 2003 Nicolai Grossman <nick@photondetector.com> and 
# contributors ( see http://recipants.photondetector.com/credits.html ) and
# the authors of Scoop
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


my $raw;

foreach(1 .. 28) {
	$raw .= chr(int(rand(255)));
}

$raw = unpack("H56", $raw);

print	"\n\n" .
		"Copy and paste the host key into your recipants.cfg.pl file\n" .
		"under $secret_host_key.\n\n" .
		"Your secret host key is:\n\n" .
		$raw .
		"\n\n\n";

exit(0);

# END keygen.pl
