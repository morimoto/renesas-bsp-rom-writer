#! /usr/bin/env python3
#===============================
#
# v3h-condor
#
# 2022/07/27 Kuninori Morimoto <kuninori.morimoto.gx@renesas.com>
#===============================
import os
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
    def __init__(self):

        self.init()

#====================================
#
# rom_write_guide
#
#====================================
class rom_write_guide(base.guide):

    #--------------------
    # main_loop
    #--------------------
    def main_loop(self):
        self.sk_type_main_loop("3", 2, self.ask_loop())

    #--------------------
    # guide_start
    #--------------------
    def guide_start(self, board):
        self.init(board)

        # chech mot file
        mot_file = self.board().mot_file()

        # make sure board is power off
        self.print_msg_power("OFF")
        self.ask_yn()

        # indicate dip-switch update mode
        self.sw().print_msg_update()
        self.ask_yn()

        self.print_msg_power("ON")
        self.expect("please send !")
        self.send_file(mot_file)
        self.expect(">")

        # main loop
        self.main_loop()

        # power off
        self.print_msg_power("OFF")
        self.ask_yn()

        # indicate dip-switch normal mode
        self.sw().print_msg_normal()
        self.ask_yn()

        # baudrate settings
        self.msg("finished !!")

#====================================
#
# As command
#
#	> condor	# test
#	> condor sdk	# SDK
#
#====================================
if __name__=='__main__':
    rom_write_guide().guide_start(board())
