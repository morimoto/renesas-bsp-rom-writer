#! /usr/bin/env python3
#===============================
#
# x5h-ironhide
#
# 2025/07/09 Kuninori Morimoto <kuninori.morimoto.gx@renesas.com>
#===============================
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

        self.init_with_mot("x5h", "sdk", "", "", baudrate=1843200)

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
        map = self.board().addr_map()
        sw = base.switch(self.board().dir_config("sw"))

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
        self.expect("W N:>")

        self.iron_type_main_loop()

        # power off
        self.power("OFF")
        self.ask_yn()

        # indicate dip-switch normal mode
        sw.print_msg_normal()
        self.ask_yn()

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
    rom_write_guide(board()).guide_start()
