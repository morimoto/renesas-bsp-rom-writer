#! /usr/bin/env python3
#===============================
#
# s4-spider
#
# 2022/02/25 Kuninori Morimoto <kuninori.morimoto.gx@renesas.com>
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
    def __init__(self, speed, board, ver="", tty=""):

        super().__init__(soc="s4", rom="sdk", board=board, ver=ver, tty=tty)

        self.speed = speed

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
        super().__init__(board.tty(), board.speed)
        # possible to use from child-class
        self.board = board

    #--------------------
    # guide_start
    #--------------------
    def guide_start(self):
        sw = base.switch(self.board.dir_config("sw"))

        # chech mot file
        mot_file = self.board.mot_file()
        self.board.check_mot(mot_file)

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
        self.sk_type_main_loop(self.board.addr_map(), "1", 2, ask)
        self.wh_type_emmc_loop(self.board.emmc_map(), "1", 1, ask)

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
#	> spider ""		# test
#	> spider sdk		# Linux BSP
#
#====================================
if __name__=='__main__':
    if (len(sys.argv) < 2):
        # test
        board(1843200, ver="Pre-Alpha4.0", tty="/dev/ttyUSB0")
    elif (sys.argv[1] == "s4_sk"):
        rom_write_guide(board(921600, sys.argv[1])).guide_start()
    elif (sys.argv[1] == "s4_spider"):
        self.msg("*NOTE1*\n\n"\
                 "The board which serial number No.2023 - No.2132\n"\
                 "needs CPLD setting to enable SW8.\n"\
                 "And baudrate = 1843200.\n"\
                 "This script is assuming this settings has already done.\n"\
                 "If not, please see Startup Guide")
        self.ask_yn()

        self.msg("*NOTE2*\n\n"\
                 "We don't know why but it seems it will hung up on some PC\n"\
                 "during sending file to Spider board.  Please check README\n"\
                 "if it doesn't finish sending file in 5 min.")
        self.ask_yn()

        rom_write_guide(board(1843200, sys.argv[1])).guide_start()

        self.msg("\n"\
                 "One note is that IPL is using 1843200 baudrate,\n"\
                 "But *default* U-Boot is using  115200 baudrate\n\n"\
                 "You can update U-Boot baudrate by\n"\
                 " 1) Connect board via baudrate 115200\n"\
                 " 2) Power ON\n"\
                 " 3) Change baudrate to 1843200, and save it\n"\
                 "      .. boot U-boot...\n"\
                 "      => setenv baudrate 1843200\n"\
                 "      => saveenv\n")
    else:
        print("unknown command")
