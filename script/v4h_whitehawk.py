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
    def __init__(self, board, tty=""):

        self.init("sdk", tty, 921600, board)

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
        board(tty="/dev/ttyUSB0")
    elif (sys.argv[1] == "sdk"):
        s4_spider.rom_write_guide().guide_start(board(sys.argv[2]))
    else:
        print("unknown command")
