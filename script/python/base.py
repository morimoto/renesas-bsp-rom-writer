#! /usr/bin/env python3
#===============================
#
# base
#
# 2022/01/06 Kuninori Morimoto <kuninori.morimoto.gx@renesas.com>
#===============================
import sys
import os
import re
import subprocess
import serial
import time
import getpass

#====================================
#
# base
#
# it supports do/run/run1 for using external command
#
#====================================
class base:
    __top = os.path.abspath(__file__ + "/../../../");
    __cwd = os.getcwd()

    #--------------------
    # top
    # cwd
    #--------------------
    def top(self): return base.__top
    def cwd(self): return base.__cwd

    #--------------------
    # tolist()
    #--------------------
    def tolist(self, string):
        if (len(string) > 0):
            return string.split('\n');

        return [];

    #--------------------
    # run()
    #
    # run command and get result as plane text
    #--------------------
    def run(self, command):

        # Ughhhh
        # I don't like python external command !!
        # (ノ `Д´)ノ  go away !!
        result = subprocess.run(command, shell=True, stdout=subprocess.PIPE)

        return result.stdout.decode("utf-8").rstrip("\n")

    #--------------------
    # runl()
    #
    # run command and get result as list
    #--------------------
    def runl(self, command):

        # call run() and exchange result as array
        #
        # "xxxxxxx
        #  yyyyyyy
        #  zzzzzzz"
        # ->
        # ["xxxxxxx",
        #  "yyyyyyy",
        #  "zzzzzzz"]
        return self.tolist(self.run(command));

    #--------------------
    # ttm_array
    # read TeraTerm array
    #--------------------
    def ttm_array(self, file, tag):
        return self.runl("grep -w \"^{}\" {} | cut -d \"=\" -f 2 | sed -e \"s/^ *\\\"//g\" | sed -e \"s/\\\"\$//g\"".format(tag, file))

    #--------------------
    # input
    #--------------------
    def input(self, console):
        try:
            return input(console)
        except KeyboardInterrupt:
            sys.exit(1)

    #--------------------
    # select("message", ["hoge", "pkuku"])
    #--------------------
    def select(self, text, list):
        max = len(list)
        if (max == 1):
            return list[0]

        for i in range(max):
            text += "\n  {}) ".format(i + 1) + list[i]

        while 1:
            self.msg(text)
            try:
                ret = int(self.input("select number (1-{}): ".format(max)))
            except:
                ret = -1
            if (ret < 0 or ret > max):
                self.error("select number in 1 - {}".format(max), quit=0)
            else:
                return list[ret - 1]

    #--------------------
    # ask_yn
    #--------------------
    def ask_yn(self, quit=None):
        ret = self.input("OK? (y/n): ")
        print()
        ret = (ret == "y")
        if (quit and not ret):
            sys.exit(1)
        return ret

    #--------------------
    # error
    #--------------------
    def error(self, text, quit=1):
        print()
        print("********* [error] *************")
        for txt in text.split("\n"):
            print("* {}".format(txt))
        print("*******************************")
        if (quit):
            sys.exit(1)
        else:
            self.ask_yn()

    #--------------------
    # msg
    #--------------------
    def msg(self, text):
        l = 0
        for txt in text.split("\n"):
            t = len(txt)
            if (t > l): l = t

        print()
        print("+-", end="")
        for i in range(l):
            print("-", end="")
        print("-+")

        for txt in text.split("\n"):
            print("| %-{}s |".format(l) % txt)

        print("+-", end="")
        for i in range(l):
            print("-", end="")
        print("-+")

#====================================
#
# switch
#
#====================================
class switch(base):

    #--------------------
    # __init__
    #--------------------
    def __init__(self, file):

        #
        # read dipswitch config from file
        #
        # dipswitch_update[..] = "....."
        # dipswitch_update[..] = "....."
        #
        # dipswitch_normal[..] = "....."
        # dipswitch_normal[..] = "....."
        #
        b = base()
        self.__head   = b.ttm_array(file, "sw_head")
        self.__update = b.ttm_array(file, "sw_update")
        self.__normal = b.ttm_array(file, "sw_normal")

    #--------------------
    # print_msg
    #--------------------
    def print_msg(self, array):
        text =  "Setup Dip-Switch as follow\n"
        text += "\n".join(self.__head)
        text += "\n"
        text += "\n".join(array)
        self.msg(text)

    #--------------------
    # print_msg_update
    # print_msg_normal
    #--------------------
    def print_msg_update(self): self.print_msg(self.__update)
    def print_msg_normal(self): self.print_msg(self.__normal)

#====================================
#
# addr_map
#
#====================================
class addr_map:

    #--------------------
    # __init__
    #--------------------
    def __init__(self, file):
        #
        # read addr_map file
        #
        # addr_map[0] = "E6320000,000000,bootparam_sa0.srec"
        # addr_map[1] = "E6304000,040000,bl2-salvator-x.srec"
        # addr_map[2] = ...
        #
        self.__addr_map = []
        b = base()
        map = b.ttm_array(file, "addr_map")
        for m in map:
            am = m.split(',')
            self.__addr_map.append({"addr":am[0],
                                    "save":am[1],
                                    "srec":am[2]})

    #--------------------
    # __iter__
    #--------------------
    def __iter__(self):
        self.__iter = 0
        return self

    #--------------------
    # __next__
    #--------------------
    def __next__(self):
        if self.__iter >= len(self.__addr_map): raise StopIteration
        ret = self.__addr_map[self.__iter]
        self.__iter += 1
        return ret

    #--------------------
    # __getitem__
    #--------------------
    def __getitem__(self, idx):
        if (idx >= len(self.__addr_map)):
            return []
        return self.__addr_map[idx]

    #--------------------
    # len
    #--------------------
    def len(self):
        return len(self.__addr_map)

#====================================
#
# board
#
#====================================
class board(base):

    #--------------------
    # __init__
    #--------------------
    def __init__(self, board,
                 soc=None, os=None, ver=None, tty=None, mode=None, mac=None, mot_file=None):

        # None   : not use
        # ""     : be used, but not yet selected
        # "xxx"  : be used, and selected
        self.__board	= board
        self.__soc	= soc
        self.__os	= os
        self.__ver	= ver
        self.__tty	= tty
        self.__mode	= mode		# normal, mot

        # for Android
        self.__mac	= mac

        # for mot mode
        self.__mot	= None		# enable mot mode if file exist
        if (mot_file):
            dir = self.ttm_array(self.dir_config(mot_file), "dir_mot")
            mot = self.ttm_array(self.dir_config(mot_file), "mot")
            self.__mot = "{}/{}".format(dir[0], mot[0])

        # for inside
        self.__config	= ".renesas_bsp_rom_writer.{}".format(board)
        self.__addr_map	= None

    #--------------------
    # mode_explanation
    # soc_explanation
    #--------------------
    def mode_explanation(self): return ""
    def soc_explanation(self):  return ""

    #--------------------
    # mode
    # board
    # tty
    # soc
    # addr_map
    # mac
    # mot
    #--------------------
    def mode(self):	return self.__mode
    def board(self):	return self.__board
    def tty(self):	return self.__tty
    def soc(self):	return self.__soc
    def os(self):	return self.__os
    def addr_map(self):	return self.__addr_map
    def mac(self):	return self.__mac
    def mot(self):	return "{}/script/flash_writer/{}".format(self.top(), self.__mot)

    #--------------------
    # soc_ws : h3_4g
    # soc    : h3
    # ws     : 4g
    #--------------------
    def __sw(self):    return re.match("(.*)_(.*)", self.__soc)
    def soc_ws(self):  return self.__soc
    def soc(self):
        m = self.__sw()
        return m.group(1) if (m) else self.__soc
    def ws(self):
        m = self.__sw()
        return m.group(2) if (m) else ""

    #--------------------
    # dir_xxx
    #--------------------
    def dir_board(self, path="", full=1):
        dir = "{}/".format(self.top()) if (full) else ""
        return "{}{}/{}".format(dir, self.__board, path)
    def dir_config(self, path="", full=1):	return self.dir_board("config/" + path, full)
    def dir_config_os(self, path="", full=1):	return self.dir_config("os/{}/{}".format(self.__os, path), full)
    def dir_config_sw(self, path="", full=1):	return self.dir_config("sw/" + path, full)

    #--------------------
    # config_xxx
    #--------------------
    def config_file(self):
        return "{}/{}".format(self.cwd(), self.__config)

    def config_read(self, tag):
        return self.run("grep \"^\[{}\]:\" {} 2>/dev/null | cut -d \":\" -f 2-".format(tag, self.config_file()))

    def config_write(self, tag, data):
        tmp = "/tmp/renesas-bsp-rom-writer-config-{}".format(os.getpid())
        if (os.path.exists(self.config_file())):
            self.run("grep -v \"^\[{}\]:\" {} > {}".format(tag, self.config_file(), tmp))
        self.run("echo \"[{}]:{}\" >> {}".format(tag, data, tmp))
        self.run("mv -f {} {}".format(tmp, self.config_file()))
        if (not os.path.exists(self.config_file())):
            self.error("cann't save configs")

    def config_load(self):
        # __init__() set default value
        # lood config if value was ""
        if (self.__soc  == ""): self.__soc  = self.config_read("soc")
        if (self.__os   == ""): self.__os   = self.config_read("os")
        if (self.__ver  == ""): self.__ver  = self.config_read("version")
        if (self.__tty  == ""): self.__tty  = self.config_read("tty")
        if (self.__mac  == ""): self.__mac  = self.config_read("mac")
        if (self.__mode == ""): self.__mode = self.config_read("mode")

    def config_save(self):
        if (self.__soc  is not None): self.config_write("soc",     self.__soc)
        if (self.__os   is not None): self.config_write("os",      self.__os)
        if (self.__ver  is not None): self.config_write("version", self.__ver)
        if (self.__tty  is not None): self.config_write("tty",     self.__tty)
        if (self.__mac  is not None): self.config_write("mac",     self.__mac)
        if (self.__mode is not None): self.config_write("mode",    self.__mode)

    #--------------------
    # setup
    #
    # overwrite select_xx() on each board
    # if default select_xx() was not good match
    #--------------------
    def setup(self):
        if (self.__os   is not None): self.__select_os()
        if (self.__ver  is not None): self.__select_ver()
        if (self.__soc  is not None): self.__select_soc()
        if (self.__tty  is not None): self.__select_tty()
        if (self.__mac  is not None): self.__select_mac()
        if (self.__mode is not None): self.__select_mode()

    #--------------------
    # select_os (default)
    #--------------------
    def __select_os(self):
        # check os/${os}/config file
        while (not os.path.exists(self.dir_config_os("config"))):
            self.__os = self.select("Select write OS", self.runl("ls {}".format(self.dir_config("os"))))

    #--------------------
    # select_ver (default)
    #--------------------
    def __select_ver(self):
        list_version = self.ttm_array(self.dir_config_os("config"), "list_version")
        while (not self.__ver in list_version):
            self.__ver = self.select("Select [{}] Version".format(self.os()), list_version)

    #--------------------
    # select_soc (default)
    #--------------------
    def __select_soc(self):
        list_soc     = self.ttm_array(self.dir_config("soc"), "list_soc")
        list_version = self.ttm_array(self.dir_config_os("config"), "list_version")
        list_map     = self.ttm_array(self.dir_config_os("config"), "list_map")

        if (not self.__ver in list_version):
            self.error("select version first")

        dir_map = self.dir_config_os(list_map[list_version.index(self.__ver)])
        text = "Select write SoC/WS\n\n" + self.soc_explanation()

        while (not os.path.isfile("{}/{}".format(dir_map, self.__soc))):
            self.__soc = self.select(text, list_soc)
        self.__addr_map = addr_map("{}/{}".format(dir_map, self.__soc))

    #--------------------
    # select_tty (default)
    #--------------------
    def __tty_error(self):
        if (not os.path.exists(self.__tty)):
            return 1

        m = re.match("/dev/tty.*", self.__tty)
        if (not m):
            return 1

        if (not os.access(self.__tty, os.R_OK) or
            not os.access(self.__tty, os.W_OK)):
            self.msg("You don't have permission to access to {}.\n".format(self.__tty) +\
                     "It requires root or \"dialout group\" permission, maybe ?\n" +\
                     "Check it\n" \
                     "   > ls -l {}\n\n".format(self.__tty) +\
                     "Check your joined group\n" \
                     "   > id\n\n" \
                     "Let's join to \"dialout group\"\n" \
                     "   > sudo gpasswd -a {} dialout\n\n".format(getpass.getuser()) +\
                     "Maybe you need to logout and login again.\n" \
                     "Then, check your joined group.\n" \
                     "   > id\n\n" \
                     "Retry to call this script if all are OK")
            sys.exit(1)
            return 1

    def __select_tty(self):
        text = "Your board and PC need to connect\n" +\
               self.tty_connection() + "\n\n"\
               "Which tty is connected to board ?\n" +\
               "  ex) /dev/ttyUSBx\n\n" +\
               "You can confirm it by this command maybe ?\n" +\
               "  > dmesg | grep ttyUSB"

        while (self.__tty_error()):
            print("\n")
            self.msg(text)
            self.__tty = self.input("ex) /dev/ttyUSBx: ")
            print()
            if (self.__tty_error()):
                self.error("{} is not exist or not tty\n".format(self.__tty) +
                           "Please select like /dev/ttyUSBx", quit=0)
            else:
                fuser = self.run("fuser -u {} 2>&1".format(self.__tty))
                if (fuser):
                    m = re.match(".*\((.*)\)", fuser)
                    self.error("{} is using {}\n".format(m.group(1), self.__tty) +
                               "Please stop using it first")

    #--------------------
    # select_mac (default)
    #--------------------
    def __select_mac(self):
        macaddr_format = "[0-9a-f]{2}:[0-9a-f]{2}(:[0-9a-f]{2}){4}$"

        while 1:
            if (re.match(macaddr_format, self.__mac.lower())):
                self.__mac = self.__mac.lower()
                return
            else:
                self.msg("Please set your board MAC address.\n"\
                         "You can find it on Ether connecter.\n\n"\
                         "Require format is\n"\
                         "    12:34:56:78:9a:bc")
                print("             xx:xx:xx:xx:xx:xx")
                self.__mac = self.input("mac address: ")

    #--------------------
    # select_mode (default)
    #--------------------
    def __select_mode(self):
        mode_list = ["normal"]

        # add more mode here
        if (self.__mot): mode_list.append("mot")

        if (self.__mode in mode_list):
            return

        if (len(mode_list) <= 1):
            self.__mode = mode_list[0]
        else:
            self.__mode = self.select("You can select ROM writer mode.\n\n" +\
                                      self.mode_explanation(), mode_list)
            print()

    #--------------------
    # print_info
    #--------------------
    def __print_info(self):
        text = "Your selected settings are...\n\n" + \
               "  [Board]:   {}\n".format(self.__board)

        deep = 0
        if (self.__soc  is not None): text += "  [SoC/WS]:  {}\n".format(self.__soc)
        if (self.__os   is not None): text += "  [OS]:      {}\n".format(self.__os)
        if (self.__ver  is not None): text += "  [Version]: {}\n".format(self.__ver)
        if (self.__mode is not None): text += "  [Mode]:    {}\n".format(self.__mode)
        if (self.__tty  is not None): text += "* [TTY]:     {}\n".format(self.__tty); deep = 1
        if (self.__mac  is not None): text += "* [MAC]:     {}\n".format(self.__mac); deep = 1

        if (deep):
            text += "\nPlease deeply check at * items\n"

        text += "\nYou can manually setup if you want\n" +\
                "   > vi ./{}\n".format(self.__config)

        if (self.__addr_map is not None):
            text += "\nAddr      Save    Srec\n"
            for m in self.__addr_map:
                text += "{}  {}  {}\n".format(m["addr"], m["save"], m["srec"])

        self.msg(text)

    #--------------------
    # confirm_location
    #--------------------
    def confirm_location(self):
        # check config file.
        # If not exist, confirm_location
        if (os.path.exists(self.config_file())): return

        self.msg("This script requires be called from {} ROM directory.\n".format(self.os()) +\
                 "Are you calling this script from there ?\n\n" +\
                 "  > cd ${{{0} ROM dir}}\n".format(self.os()) +\
                 "  > ${{renesas-bsp-rom-writer}}/{}/linux/{}-writer".format(self.board(), self.os()))
        self.ask_yn(quit=True)

    #--------------------
    # confirm_info
    #--------------------
    def confirm_info(self):
        while 1:
            self.__print_info()
            if (self.ask_yn()): break;

            # reset all setting
            # ignore os here
            if (self.__soc  is not None): self.__soc  = ""
            if (self.__ver  is not None): self.__ver  = ""
            if (self.__tty  is not None): self.__tty  = ""
            if (self.__mac  is not None): self.__mac  = ""
            if (self.__mode is not None): self.__mode = ""
            self.setup()

    #--------------------
    # check_srec
    #--------------------
    def __check_srec(self):
        if (not self.__addr_map): return

        err = ""
        for m in self.__addr_map:
            if (not os.path.exists("{}/{}".format(self.cwd(), m["srec"]))):
                err += "  {}\n".format(m["srec"])

        if (len(err)):
            self.error("These files are required, but not found.\n\n" +
                       err + "\n" +
                       "Please goto binary dir and retry this command.\n" +
                       "You can reuse setting if you want.\n\n" +
                       "	> mv ./{} ${{binary_dir}}\n".format(self.__config) +
                       "	> cd ${binary_dir}\n"
                       "	> ${renesas-bsp-rom-writer}/xxx # retry\n")

    #--------------------
    # check_mot
    #--------------------
    def __check_mot(self):
        if (not self.__mot): return
        if (not self.mode() == "mot"): return

        if (not os.path.isfile(self.mot())):
            self.error("You selected mot mode to write ROM.\n"\
                       "It needs mot file, but you didn't create it yet.\n"\
                       "Please run make and create mot file.\n\n"\
                       "   > cd ${renesas-bsp-rom-writer}\n"\
                       "   > make\n\n"\
                       "You need is\n" + self.mot())

    #--------------------
    # check_files
    #--------------------
    def check_files(self):
        self.__check_srec()
        self.__check_mot()

#====================================
#
# guide
#
#====================================
class guide(base):

    #--------------------
    # __init__
    #--------------------
    def __init__(self, tty, baudrate):
        # for guide
        self.__serial		= None
        self.__line_array	= []
        self.__remain_lines	= ""

        self.__serial = serial.Serial(
            port	= tty,
            baudrate	= baudrate,
            bytesize	= serial.EIGHTBITS,
            parity	= serial.PARITY_NONE,
            stopbits	= serial.STOPBITS_ONE)

    #--------------------
    # __load_input
    #--------------------
    def __load_input(self):
        size = self.__serial.inWaiting()
        if (not size): return

        line = self.__serial.read(size).decode(errors='ignore')
        print(line, end="", flush=True)
        self.__remain_lines += line
        array = self.__remain_lines.split("\n")
        last  = len(array) - 1

        if (array[last] is None):
            self.__remain_lines = ""
        else:
            self.__remain_lines = array.pop(last)

        self.__line_array += array

    #--------------------
    # __expect
    #--------------------
    def __expect(self, pattern):
        while len(self.__line_array) > 0:
            line = self.__line_array.pop(0)
            if (pattern in line):
                return True
        idx = self.__remain_lines.find(pattern)
        if (idx >= 0):
            self.__remain_lines = self.__remain_lines[idx + len(pattern):]
            return True
        return False

    #--------------------
    # ___expect
    #--------------------
    def ___expect(self, pattern, timeout=60):
        timeout += int(time.time())
        try:
            while int(time.time()) < timeout:
                # load new input if exists
                self.__load_input()
                # check pattern
                if (self.__expect(pattern)):
                    return True
                else:
                    time.sleep(0.2)
        except KeyboardInterrupt:
            sys.exit(1)

        return False

    #--------------------
    # expect
    #--------------------
    def expect(self, pattern, timeout=60):
        if (not self.___expect(pattern, timeout)):
            self.error("expect timeout")

    #--------------------
    # stop_autorun
    #--------------------
    def stop_autorun(self, timeout=60):
        timeout += int(time.time()) + 10
        while int(time.time()) < timeout:
            self.send()
            if (self.___expect("=>", 0.5)):
                return True
        self.error("couldn't stop autorun")

    #--------------------
    # send
    # send_file
    #--------------------
    def send(self, cmd="", end="\r"):
        return self.__serial.write("{}{}".format(cmd, end).encode())
    def send_file(self, file):
        self.msg("Now it is sending below file to board.\n"\
                 "Please wait.\n"\
                 "[{}]".format(os.path.basename(file)))
        with open(file, "rb") as f:
            self.__serial.write(f.read())
        self.send("\n", end="")

    #--------------------
    # speed_up
    #--------------------
    def speed_up(self, pattern, baudrate):
        self.send()
        self.expect(">")

        self.send("sup")
        self.expect(pattern)

        self.__serial.baudrate = baudrate

    #--------------------
    # power
    #--------------------
    def power(self, onoff):
        self.msg("Power {}".format(onoff))

#====================================
#
# As command
#
# test
#	base.py base
#	base.py switch
#	base.py map
#
#====================================
if __name__=='__main__':
    b = base()
    if (sys.argv[1] == "base"):
        #
        # base
        #
        print(b.top())
        print(b.run("ls"))
        print(b.runl("ls"))
    elif (sys.argv[1] == "switch"):
        #
        # switch
        #
        sw = switch(b.top() + "/starterkit/config/sw/h3")
        sw.print_msg_update()
        sw.print_msg_normal()
    elif (sys.argv[1] == "map"):
        #
        # addr_map
        #
        map = addr_map(b.top() + "/starterkit/config/os/yocto/map01/h3_4g")

        print("addr      save    srec")
        for i in range(map.len()):
            print("{}  {}  {}".format(map[i]["addr"], map[i]["save"], map[i]["srec"]))

        print("addr      save    srec")
        for m in map:
            print("{}  {}  {}".format(m["addr"], m["save"], m["srec"]))
