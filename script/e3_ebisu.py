#! /usr/bin/env python3
#===============================
#
# e3-ebisu
#
# 2022/03/24 Kuninori Morimoto <kuninori.morimoto.gx@renesas.com>
#===============================
import sys
import time

import base
#====================================
#
# board
#
#====================================
class board(base.board):
    #--------------------
    # __init__
    #--------------------
    def __init__(self, board, soc="", ver="", tty=""):

        self.init(soc=soc, rom="yocto", ver=ver, tty=tty, board=board)

#====================================
#
# rom_write_guide
#
#====================================
class rom_write_guide(base.guide):
    #--------------------
    # guide_start
    #--------------------
    def guide_start(self, board):
        self.init(board)

        sw = base.switch(board.dir_config("config"))

        # make sure board is power off
        self.print_msg_power("OFF")
        self.ask_yn()

        # indicate dip-switch update mode
        sw.print_msg_update()
        self.ask_yn()

        self.print_msg_power("ON")
        self.expect(">")

        # indicate dip-switch normal mode
        sw.print_msg_normal()
        self.ask_yn()

        # speed up
        self.speed_up("921.6Kbps", 921600)

        # main loop
        self.sk_type_main_loop("3", 3, self.ask_loop())
        self.msg("finished !!")

#====================================
#
# As command
#
#	> ebisu yocto		# yocto
#	> ebisu			# test
#
#====================================
if __name__=='__main__':
    board_name = sys.argv[1]
    if (len(sys.argv) < 2):
        # test
        board(soc="ebisu_4d", ver="5.9.0", tty="/dev/ttyUSB0")
        sys.exit(0)
    if (sys.argv[2] == "yocto"):
        rom_write_guide().guide_start(board(board_name))
    else:
        print("unknown command")
