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
import s4_spider
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

        self.init_with_mot(soc, "sdk", ver, tty, 921600, board)

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
        s4_spider.rom_write_guide(board(sys.argv[2])).guide_start()
    else:
        print("unknown command")
