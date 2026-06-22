#! /usr/bin/env python3
#===============================
#
# m3le-geist
#
# 2026/04/14 Kuninori Morimoto <kuninori.morimoto.gx@renesas.com>
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
    def __init__(self):

        self.init_with_mot("m3le", "yocto", "", "", 115200, "m3le_geist")

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
        self.sk_type_main_loop("1", 4, ask)

#====================================
#
# As command
#
#====================================
if __name__=='__main__':
    rom_write_guide().guide_start(board())
