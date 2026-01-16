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
    # guide_start
    #--------------------
    def guide_start(self, board):
        self.init(board)

        sw = base.switch(board.dir_config("config"))

        # chech mot file
        mot_file = board.mot_file()

        # power off
        self.power("OFF")
        if not self.auto_power_off():
            self.ask_yn()

        # indicate dip-switch update mode
        sw.print_msg_update()
        if not self.auto_config_flash():
            self.ask_yn()

        self.power("ON")
        self.auto_power_on()
        self.expect("please send !")
        self.send_file(mot_file)
        self.expect(" N:>")

        ask = self.ask_loop()
        self.iron_type_main_loop(ask, "addr_map", "hyper_write_srec")
        self.iron_type_main_loop(ask, "ufs_map",  "ufs_write_srec")

        # power off
        self.power("OFF")
        if not self.auto_power_off():
            self.ask_yn()

        # indicate dip-switch normal mode
        sw.print_msg_normal()
        if not self.auto_config_boot():
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
    rom_write_guide().guide_start(board())
