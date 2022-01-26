#! /usr/bin/env python3
#===============================
#
# salvator
#
# 2022/01/19 Kuninori Morimoto <kuninori.morimoto.gx@renesas.com>
#===============================
import sys

import base
import starterkit
#====================================
#
# board
#
#====================================
class board(base.board):
    #--------------------
    # __init__
    #--------------------
    def __init__(self, confirm, soc="", os="", ver="", tty="", mac=None):

        # mac is needed if Android
        if (os == "android"):
            mac = ""
        # mot setting file for dir_config()
        mot_file = "mot"

        super().__init__("salvator", soc=soc, os=os, ver=ver, tty=tty, mac=mac, mode="", mot_file=mot_file)

        self.confirm_location()
        self.config_load()
        self.setup()

        # confirm to user
        if (confirm):
            self.confirm_info()
        self.config_save()
        self.check_files()

    #--------------------
    # tty_connection
    # soc_explanation
    # mode_explanation
    #--------------------
    def tty_connection(self):
        return "\n".join(self.ttm_array(self.dir_config_os("connection"), "tty_connection"))
    def soc_explanation(self):
        return "\n".join(self.ttm_array(self.dir_config("soc"), "list_soc_explanation"))
    def mode_explanation(self):
        # We can't share mode explanation message on config file
        # because Linux vs Windows explanation are different
        return "normal: Need Dip-Switch settings at both Front/Back side\n" +\
               "        to write ROM. You need to select normal mode\n" +\
               "        if your current board has no ROM (no U-boot).\n" +\
               "mot:    Need Dip-Switch settings at only Front side.\n" +\
               "        You need to run make and create mot first.\n" +\
               "             > cd ${renesas-bsp-rom-writer}\n" +\
               "             > make\n"

#====================================
#
# rom_write_guide
#
# Salvator / Starterkit are almost same.
# reuse Starterkit guide with some overwrite
#====================================
class rom_write_guide(starterkit.rom_write_guide):

    #======================
    # <Overwrite>
    #
    # load_sw
    #
    # salvator sw setting are located at
    # ${renesas-bsp-rom-writer}/starterkit/config/sw/${mode}
    #======================
    def load_sw(self):
        return base.switch(self.board.dir_config_sw(self.board.mode()))

    #======================
    # <Overwrite>
    #
    # Salvator always need 2nd Y in main loop
    #======================
    def use_2nd_Y(self):
        return True

    #======================
    # <Overwrite>
    #
    # guide_for_mot
    #======================
    def guide_for_mot(self):
        sw = self.load_sw()

        # indicate dip-switch update mode
        sw.print_msg_update()
        self.ask_yn()

        # power on
        self.power("ON")
        self.expect("please send !")

        # indicate meesage
        # and send mot file
        self.send_file(self.board.mot())
        self.expect(">")

        # speed up
        self.speed_up("921.6Kbps", 921600)

        # main loop
        self.main_loop()

        # back dip-switch normal mode
        sw.print_msg_normal()
        self.ask_yn()

#====================================
#
# As command
#
#	> salvator yocto		# yocto
#	> salvator android		# android
#	> salvator --			# select os
#	> salvator android_fastboot	# android fastboot for uboot
#	> salvator			# test
#
#====================================
if __name__=='__main__':
    confirm	= 0
    os		= ""
    guide	= None

    if (not sys.argv[1]):
        # test
        board("h3_4g", os="yocto", ver="5.5.0", tty="/dev/ttyUSB0")
        sys.exit(0)
    if (sys.argv[1] == "yocto"):
        confirm = 1
        os = "yocto"
        guide = rom_write_guide
    elif (sys.argv[1] == "android"):
        confirm = 1
        os = "android"
        guide = rom_write_guide
    elif (sys.argv[1] == "android_fastboot"):
        confirm = 0
        os = "android"
        # reuse starterkit fastboot
        guide = starterkit.fastboot_uboot_guide
    else:
        print("unknown command")
        sys.exit(1)

    guide(board(confirm, os=os)).guide_start()
