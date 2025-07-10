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
    # mot_file
    # mot_error
    #--------------------
    def mot_file_raw(self):
            return self.ttm_array(self.map(), "mot_file")[0]

    def mot_file(self):
        return "{}/{}".format(self.cwd(), self.mot_file_raw())

    def mot_error(self):
        self.error("It seems you don't have necessary mot file\n" +\
                   "({})\n".format(self.mot_file_raw()) +\
                   "Please re-check current dir")

    #--------------------
    # init_with_mot
    #--------------------
    def init_with_mot(self, soc, rom, ver, tty, baudrate=115200, board=None):

        self.init(soc=soc, rom=rom, ver=ver, tty=tty, mode="mot", baudrate=baudrate, board=board)

    #--------------------
    # __init__
    #--------------------
    def __init__(self, ver="", tty=""):

        self.gen4_init("v4h2", "sdk", ver, tty)

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
    # main_loop
    #--------------------
    def main_loop(self):
        self.sk_type_main_loop("3", 2, self.ask_loop())

    #--------------------
    # guide_start
    #--------------------
    def guide_start(self):
        sw = base.switch(self.board().dir_config("config"))

        # chech mot file
        mot_file = self.board().mot_file()

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
        self.main_loop()

        # power off
        self.power("OFF")
        self.ask_yn()

        # indicate dip-switch normal mode
        sw.print_msg_normal()
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
    if (len(sys.argv) < 2):
        # test
        board(ver="3.3.0", tty="/dev/ttyUSB0")
    elif (sys.argv[1] == "sdk"):
        rom_write_guide(board()).guide_start()
    else:
        print("unknown command")
