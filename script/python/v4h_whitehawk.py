#! /usr/bin/env python3
#===============================
#
# v4h-whitehawk
#
# 2022/08/23 Kuninori Morimoto <kuninori.morimoto.gx@renesas.com>
#===============================
import os
import sys
import time

import base
import v3h_condor
#====================================
#
# board
#
#====================================
class board(v3h_condor.board):
    #--------------------
    # __init__
    #--------------------
    def __init__(self, board, ver="", tty=""):

        soc = board.split("_")[0] # v4h_whitehawk

        self.gen3_init(soc, "sdk", ver, tty, 921600, board)

#====================================
#
# rom_write_guide
#
#====================================
class rom_write_guide(base.guide):

    #--------------------
    # __init__
    #--------------------
    def __init__(self, board):
        super().__init__(board)

    #--------------------
    # guide_start
    #--------------------
    def guide_start(self):
        sw = base.switch(self.board().dir_config("sw"))

        # chech mot file
        mot_file = self.board().mot_file()
        self.board().check_mot(mot_file)

        # power off
        self.power("OFF")
        self.ask_yn()

        # indicate dip-switch update mode
        sw.print_msg_update()
        self.ask_yn()

        self.power("ON")
        self.expect("please send !")
        self.send_file(mot_file)
        self.expect(">")

        # main loop
        ask = self.ask_loop()
        self.sk_type_main_loop(self.board().addr_map(), "1", 2, ask)
        self.wh_type_emmc_loop(self.board().emmc_map(), "1", 1, ask)

        # power off
        self.power("OFF")
        self.ask_yn()

        # indicate dip-switch normal mode
        sw.print_msg_normal()
        self.ask_yn()

        # indicate baudrate
        self.msg("it is 921600 baudrate !!")

#====================================
#
# As command
#
#	> whitehawk.py ""	# test
#	> whitehawk.py sdk	# SDK
#
#====================================
if __name__=='__main__':
    if (len(sys.argv) < 2):
        # test
        board(ver="3.0.1", tty="/dev/ttyUSB0")
    elif (sys.argv[1] == "sdk"):
        rom_write_guide(board(sys.argv[2])).guide_start()
    else:
        print("unknown command")
