#!/usr/bin/expect
# SPDX-License-Identifier: GPL-2.0
#====================================
#
# Renesas M3 StarterKit ROM Writer
#
# https://elinux.org/R-Car/Boards/M3SK#Quick_Start_How_To
#====================================

proc serial_number_check {} {
    set mem 0

    puts "**************************************"
    puts "Pleasse Select Your Board"
    puts ""
    puts "1. RTP0RC7796SKBX0010SA09  (v1.0, 2GiB)"
    puts "2. RTP8J77961ASKB0SK0SA05A (v3.0, 8GiB)"
    puts "**************************************"
    puts "No ?"
    set ans [gets stdin]

    switch $ans {
	"1"     {
	    puts "v1.0 is not supported"
	    exit 0
	}
	"2"     { }
	default { exit 0 }
    }
}

serial_number_check

#
# load settings
#
source ${top}/linux/script/${tgt}/${map}/m3
