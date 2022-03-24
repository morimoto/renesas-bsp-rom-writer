#! /usr/bin/env python3
#===============================
#
# spider
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
    # select_soc
    #--------------------
    def __select_soc(self):
        self.__select_soc_noselect()

    #--------------------
    # __init__
    #--------------------
    def __init__(self, ver="", tty="", mac=None):

        super().__init__("spider", soc="s4", os="linux-bsp", ver=ver, tty=tty, mode="normal")

        self.confirm_location()
        self.config_load()
        self.setup()

        self.confirm_info()
        self.config_save()
        self.check_files()

    #--------------------
    # tty_connection
    #--------------------
    def tty_connection(self):
        return "\n".join(self.ttm_array(self.dir_config_os("connection"), "tty_connection"))

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
        super().__init__(board.tty(), 1843200)
        # possible to use from child-class
        self.board = board

    #--------------------
    # guide_start
    #--------------------
    def guide_start(self):
        sw = base.switch(self.board.dir_config("sw"))

        # chech mot file
        mot_file = "ICUMXA_Flash_writer_SCIF_DUMMY_CERT_EB200000_spider.mot"
        if (not os.path.exists("{}/{}".format(self.cwd(), mot_file))):
            self.msg("It seems you don't have necessary mot file\n"\
                     "({})\n".format(mot_file) +\
                     "Please re-check current dir")
            self.ask_yn()
            sys.exit(1)

        # serial connection
        self.msg("Confirm serial connection.\n" +\
                 self.board.tty_connection())

        # power off
        self.power("OFF")
        self.ask_yn()

        # indicate dip-switch update mode
        sw.print_msg_update()
        self.ask_yn()

        self.power("ON")
        self.expect("please send !")
        self.send_file("{}/{}".format(self.cwd(), mot_file))
        self.expect(">")

        # main loop
        self.sk_type_main_loop(self.board.addr_map(), "1", True)

        # power off
        self.power("OFF")
        self.ask_yn()

        # indicate dip-switch normal mode
        sw.print_msg_normal()
        self.ask_yn()

        # baudrate settings
        self.msg("finished !!\n\n"\
                 "But, you might not see any U-Boot output because of\n"\
                 "baudrate settings. In such case, you need to setup\n"\
                 "U-Boot baudrate by yourself\n"\
                 " 1) Connect board via baudrate 115200\n"\
                 " 2) Power ON\n"\
                 " 3) Change baudrate to 1843200, and save it\n"\
                 "      .. boot U-boot...\n"\
                 "      => setenv baudrate 1843200\n"\
                 "      => saveenv\n")

#====================================
#
# As command
#
#	> spider ""		# test
#	> spider linux-bsp	# Linux BSP
#
#====================================
if __name__=='__main__':
    if (len(sys.argv) < 2):
        # test
        board(ver="Pre-Alpha4.0", tty="/dev/ttyUSB0")
    elif (sys.argv[1] == "linux-bsp"):
        rom_write_guide(board()).guide_start()
    else:
        print("unknown command")
