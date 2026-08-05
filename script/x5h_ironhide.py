#! /usr/bin/env python3
#===============================
#
# x5h-ironhide
#
# 2025/07/09 Kuninori Morimoto <kuninori.morimoto.gx@renesas.com>
#===============================
import base


#====================================
#
# board
#
#====================================
class board(base.board):
    #--------------------
    # __init__
    #--------------------
    def __init__(self):

        self.init(1843200, auto_cmd="x5h_ironhide/linux/rcar_board_control_x5h")

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

        # make sure board is power off
        if (board.auto_cmd_is_available()):
            board.auto_cmd("off")
        else:
            self.print_msg_power("OFF")
            self.ask_yn()

        # indicate dip-switch update mode
        if (board.auto_cmd_is_available()):
            board.auto_cmd("flash")
        else:
            self.sw().print_msg_update()
            self.ask_yn()

        # turn the board on
        if (board.auto_cmd_is_available()):
            board.auto_cmd("on")
        else:
            self.print_msg_power("ON")

        self.expect("please send !")
        self.send_mot_file()
        self.expect("N:>")

        ask = self.ask_loop()
        self.iron_type_main_loop(ask, "addr_map", "hyper_write_srec")
        self.iron_type_main_loop(ask, "ufs_map",  "ufs_write_srec")

        # power off
        if (board.auto_cmd_is_available()):
            board.auto_cmd("off")
        else:
            self.print_msg_power("OFF")
            self.ask_yn()

        # indicate dip-switch normal mode
        if (board.auto_cmd_is_available()):
            board.auto_cmd("boot")
        else:
            self.sw().print_msg_normal()
            self.ask_yn()

        self.msg("finished !!")

#====================================
#
# As command
#
#====================================
if __name__=='__main__':
    rom_write_guide().guide_start(board())
