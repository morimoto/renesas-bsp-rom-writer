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
    # select_soc
    #--------------------
    def __select_soc(self):
        self.__select_soc_noselect()

    #--------------------
    # __init__
    #--------------------
    def __init__(self, board, ver="", tty=""):

        arg = board.split("_") # v4h_whitehawk

        super().__init__(soc=arg[0], rom="sdk", board=board, ver=ver, tty=tty, baudrate=921600)

        self.confirm_location()
        self.config_load()
        self.setup()

        self.confirm_info()
        self.config_save()
        self.check_files()

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
