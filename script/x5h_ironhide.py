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

        # make sure board is power off
        if (board.auto_cmd_is_supported()):
            board.auto_cmd("off")
        else:
            self.print_msg_power("OFF")
            self.ask_yn()

        # indicate dip-switch update mode
        if (board.auto_cmd_is_supported()):
            board.auto_cmd("flash")
        else:
            sw.print_msg_update()
            self.ask_yn()

        # turn the board on
        if (board.auto_cmd_is_supported()):
            board.auto_cmd("on")
        else:
            self.print_msg_power("ON")

        self.expect("please send !")
        self.send_file(mot_file)
        self.expect(" N:>")

        ask = self.ask_loop()
        self.iron_type_main_loop(ask, "addr_map", "hyper_write_srec")
        self.iron_type_main_loop(ask, "ufs_map",  "ufs_write_srec")

        # power off
        if (board.auto_cmd_is_supported()):
            board.auto_cmd("off")
        else:
            self.print_msg_power("OFF")
            self.ask_yn()

        # indicate dip-switch normal mode
        if (board.auto_cmd_is_supported()):
            board.auto_cmd("boot")
        else:
            sw.print_msg_normal()
            self.ask_yn()

        self.msg("finished !!")

#====================================
#
# As command
#
#====================================
if __name__=='__main__':
    rom_write_guide().guide_start(board())
