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
    def __init__(self, baudrate, rom, board, ver="", tty=""):

        self.init_with_mot("s4", rom, ver, tty, baudrate, board)

#====================================
#
# rom_write_guide
#
#====================================
class rom_write_guide(v3h_condor.rom_write_guide):

    #--------------------
    # main_loop
    #--------------------
    def main_loop(self):
        ask = self.ask_loop()
        self.sk_type_main_loop(self.board().addr_map(), "1", 2, ask)
        self.wh_type_emmc_loop(self.board().emmc_map(), "1", 1, ask)

#====================================
#
# As command
#
#	> spider ""		# test
#	> spider sdk		# Linux BSP
#
#====================================
if __name__=='__main__':
    if (len(sys.argv) < 3):
        # test
        board(1843200, ver="Pre-Alpha4.0", tty="/dev/ttyUSB0")
    elif (sys.argv[2] == "s4_sk"):
        rom_write_guide(board(921600, sys.argv[1], sys.argv[2])).guide_start()
    elif (sys.argv[2] == "s4_spider"):
        board = board(1843200, sys.argv[1], sys.argv[2])
        board.msg("*NOTE1*\n\n"\
                 "The board which serial number No.2023 - No.2132\n"\
                 "needs CPLD setting to enable SW8.\n"\
                 "And baudrate = 1843200.\n"\
                 "This script is assuming this settings has already done.\n"\
                 "If not, please see Startup Guide")
        board.ask_yn()

        board.msg("*NOTE2*\n\n"\
                 "We don't know why but it seems it will hung up on some PC\n"\
                 "during sending file to Spider board.  Please check README\n"\
                 "if it doesn't finish sending file in 5 min.")
        board.ask_yn()

        rom_write_guide(board).guide_start()

        board.msg("\n"\
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
