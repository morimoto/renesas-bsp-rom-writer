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
    __top = os.path.abspath(__file__ + "/../../");
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
        return self.runl('grep -w "^{}" {} | sed -e "s/^{}: *\\"//g" | sed -e "s/\\"$//g"'.format(tag, file, tag))

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
            except KeyboardInterrupt:
                sys.exit(1)
            except ValueError:
                ret = -1
            if (ret <= 0 or ret > max):
                self.error("select number in 1 - {}".format(max), quit=0)
            else:
                return list[ret - 1]

    #--------------------
    # ask_yn
    #--------------------
    def ask_yn(self, quit=None, default=None):
        while 1:
            msg = " <default {}>: ".format(default) if (default) else ": "
            ret = self.input("OK? (y/n)" + msg)
            if (default and ret == ""):
                ret = default
            if (ret == "y"):
                return 1
            if (ret == "n"):
                if (quit):
                    sys.exit(1)
                else:
                    return 0

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
# config_map
#
#====================================
class config_map:

    #--------------------
    # __init__
    #--------------------
    def __init__(self, file, map_name):
        #
        # read addr_map file
        #
        # addr_map:"000000,bootparam_sa0.srec"
        # addr_map:"040000,bl2-salvator-x.srec"
        # addr_map:...
        #

        #
        # srec file not exist if ["addr"] was None
        #
        self.__map = []
        b = base()
        map = b.ttm_array(file, map_name)
        for m in map:
            am = m.split(',')
            addr = None
            if (os.path.exists("{}/{}".format(b.cwd(), am[1]))):
                addr = b.run("head -n 2 {}/{} | grep S3 | head -n 1 | cut -c5-12".format(b.cwd(), am[1]))
            self.__map.append({"addr":addr,
                               "save":am[0],
                               "srec":am[1]})

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
        if self.__iter >= len(self.__map): raise StopIteration
        ret = self.__map[self.__iter]
        self.__iter += 1
        return ret

    #--------------------
    # __getitem__
    #--------------------
    def __getitem__(self, idx):
        if (idx >= len(self.__map)):
            return []
        return self.__map[idx]

    #--------------------
    # len
    #--------------------
    def len(self):
        return len(self.__map)

#====================================
#
# board
#
#====================================
class board(base):

    #--------------------
    # init
    #--------------------
    def init(self, soc=None, rom=None, ver=None, tty=None, board=None, mode="normal", baudrate=115200, mac=None):

        # None   : not use
        # ""     : be used, but not yet selected
        # "xxx"  : be used, and selected
        if (board):
            self.__board = board
        else:
            self.__board = os.path.splitext(os.path.basename(sys.argv[0]))[0]
        self.__soc	= soc
        self.__rom	= rom
        self.__ver	= ver
        self.__tty	= tty
        self.__mode	= mode		# normal, mot
        self.__baudrate	= baudrate

        # for Android
        self.__mac	= mac

        # for inside
        self.__config	= ".renesas_bsp_rom_writer.{}".format(self.__board)
        self.__addr_map	= {}
        self.__map	= None
        self.__auto_cmd = None

        self.confirm_location()
        self.config_load()
        self.setup()

        self.confirm_info()
        self.config_save()

    #--------------------
    # mot_file
    #--------------------
    def mot_file(self): return None

    #--------------------
    # mode_explanation
    #--------------------
    def mode_explanation(self): return ""

    #--------------------
    # mode
    # board
    # tty
    # soc
    # mac
    # baudrate
    #--------------------
    def mode(self):	return self.__mode
    def board(self):	return self.__board
    def tty(self):	return self.__tty
    def soc(self):	return self.__soc
    def rom(self):	return self.__rom
    def map(self):	return self.__map
    def mac(self):	return self.__mac
    def baudrate(self):	return self.__baudrate

    #--------------------
    # addr_map
    #
    # addr_map()
    #	= "addr_map":{["addr": ..., "save":..., "srec":...],...}
    #	  "emmc_map":{["addr": ..., "save":..., "srec":...],...}
    #
    # addr_map("addr_map")
    #	= {["addr": ..., "save":..., "srec":...],...}
    #--------------------
    def addr_map(self, name=None):
        if (name):
            if (name in self.__addr_map):
                return self.__addr_map[name]
            else:
                return {}
        else:
            return self.__addr_map

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
        return "{}board/{}/{}".format(dir, self.__board, path)
    def dir_config(self, path="", full=1):	return self.dir_board("config/" + path, full)
    def dir_config_rom(self, path="", full=1):	return self.dir_config("rom/{}/{}".format(self.__rom, path), full)

    #--------------------
    # config_xxx
    #--------------------
    def config_file(self):
        return "{}/{}".format(self.cwd(), self.__config)

    def config_read(self, tag):
        value = self.run(r'grep "^\[{}\]:" {} 2>/dev/null | cut -d : -f 2-'.format(tag, self.config_file()))
        # Force returning None if the config setting is not defined
        if (value != ""):
            return value
        else:
            return None

    def config_write(self, tag, data):
        tmp = "/tmp/renesas-bsp-rom-writer-config-{}".format(os.getpid())
        if (os.path.exists(self.config_file())):
            self.run(r'grep -v "^\[{}\]:" {} > {}'.format(tag, self.config_file(), tmp))
        self.run("echo \"[{}]:{}\" >> {}".format(tag, data, tmp))
        self.run("mv -f {} {}".format(tmp, self.config_file()))
        if (not os.path.exists(self.config_file())):
            self.error("cann't save configs")

    def config_load(self):
        # __init__() set default value
        # load config if value was ""
        if (self.__soc  == ""): self.__soc  = self.config_read("soc")
        if (self.__rom  == ""): self.__rom  = self.config_read("rom")
        if (self.__ver  == ""): self.__ver  = self.config_read("version")
        if (self.__tty  == ""): self.__tty  = self.config_read("tty")
        if (self.__mac  == ""): self.__mac  = self.config_read("mac")
        if (self.__mode == ""): self.__mode = self.config_read("mode")
        self.__auto_cmd = self.config_read("auto_cmd")

    def config_save(self):
        if (self.__soc  is not None): self.config_write("soc",     self.__soc)
        if (self.__rom  is not None): self.config_write("rom",     self.__rom)
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
        if (self.__rom  is not None): self.__select_rom()
        if (self.__ver  is not None): self.__select_ver()
        if (self.__soc  is not None): self.__select_soc()
        if (self.__tty  is not None): self.__select_tty()
        if (self.__mac  is not None): self.__select_mac()
        if (self.__mode is not None): self.__select_mode()

    #--------------------
    # select_rom (default)
    #--------------------
    def __select_rom(self):
        # check rom/${os}/config file
        while (not os.path.exists(self.dir_config_rom("config"))):
            self.__rom = self.select("Select write OS", self.runl("ls {}".format(self.dir_config("rom"))))

    #--------------------
    # select_ver (default)
    #--------------------
    def __select_ver(self):
        list_version = self.ttm_array(self.dir_config_rom("config"), "list_version")
        while (not self.__ver in list_version):
            self.__ver = self.select("Select [{}] Version".format(self.rom()), list_version)

    #--------------------
    # select_soc (default)
    #--------------------
    def __select_soc(self):
        list_version = self.ttm_array(self.dir_config_rom("config"), "list_version")
        list_map     = self.ttm_array(self.dir_config_rom("config"), "list_map")

        if (os.path.exists(self.dir_config("soc"))):
            list_soc = self.ttm_array(self.dir_config("soc"), "list_soc")

            if (not self.__ver in list_version):
                self.error("select version first")

            dir_map = self.dir_config_rom(list_map[list_version.index(self.__ver)])
            text = "\n".join(self.ttm_array(self.dir_config("soc"), "list_soc_explanation")) + \
                   "\n\nSelect SoC/WS ROM\n"

            while (not os.path.isfile("{}/{}".format(dir_map, self.__soc))):
                self.__soc = self.select(text, list_soc)

            self.__map = "{}/{}".format(dir_map, self.__soc)
        else:
            self.__map = self.dir_config_rom(list_map[list_version.index(self.__ver)])

        for name in ["addr_map", "emmc_map", "ufs_map"]:
            map = config_map(self.__map, name)
            if (map.len()):
                self.__addr_map[name] = map

        err = ""
        for key, map in self.addr_map().items():
            for m in map:
                if (not m["addr"]):
                    err += "  {}\n".format(m["srec"])

        if (len(err)):
            self.error("These files are required, but not found.\n\n" + err)

    #--------------------
    # select_tty (default)
    #--------------------
    def tty_connection(self):
        return self.ttm_array(self.dir_config("config"), "tty_connection")[0]

    def __tty_error(self):
        if (not os.path.exists(self.__tty)):
            return 1

        m1 = re.match("/dev/tty.*",     self.__tty)
        m2 = re.match("/dev/serial/.*", self.__tty)
        if (not m1 and not m2):
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
        text = "Your board and PC need to connect\n" + self.tty_connection()
        self.msg(text)
        self.ask_yn(quit=True)

        text = "You need to stop minicom or other software\n" +\
               "which is connecting to the board"
        self.msg(text)
        self.ask_yn(quit=True)

        text = "Which tty is connected to board ?\n" +\
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
                    m = re.match('.*((.*))', fuser)
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
        if (self.mot_file()): mode_list.append("mot")

        if (not self.__mode in mode_list):
            if (len(mode_list) <= 1):
                self.__mode = mode_list[0]
            else:
                self.__mode = self.select("You can select ROM writer mode.\n\n" +\
                                          self.mode_explanation(), mode_list)
                print()

        if (self.mode() == "mot"):
            mot_file = self.mot_file()
            if (not mot_file or
                not os.path.exists(mot_file)):
                self.mot_error()

    #--------------------
    # print_info
    #--------------------
    def __print_info(self):
        text = "Your selected settings are...\n\n" + \
               "  [Board]:   {}\n".format(self.__board)

        deep = 0
        if (self.__soc  is not None): text += "  [SoC/WS]:  {}\n".format(self.__soc)
        if (self.__rom  is not None): text += "  [OS]:      {}\n".format(self.__rom)
        if (self.__ver  is not None): text += "  [Version]: {}\n".format(self.__ver)
        if (self.__mode is not None): text += "  [Mode]:    {}\n".format(self.__mode)
        if (self.__tty  is not None): text += "* [TTY]:     {} ({})\n".format(self.__tty, self.baudrate()); deep = 1
        if (self.__mac  is not None): text += "* [MAC]:     {}\n".format(self.__mac); deep = 1
        if (self.__auto_cmd is not None):   text += "  [Auto command]:     {}\n".format(self.__auto_cmd)

        if (deep):
            text += "\nPlease deeply check at * items\n"

        text += "\nYou can manually setup if you want\n" +\
                "   > vi ./{}\n".format(self.__config)

        for name in self.addr_map().keys():
            text += "\n[{}]\n".format(name)
            text += "Addr      Save    Srec\n"
            for m in self.addr_map(name):
                text += "{}  {}  {}\n".format(m["addr"], m["save"], m["srec"])

        self.msg(text)

    #--------------------
    # confirm_location
    #--------------------
    def confirm_location(self):
        # check config file.
        # If not exist, confirm_location
        if (os.path.exists(self.config_file())): return

        self.msg("This script requires be called from {} ROM directory.\n".format(self.rom()) +\
                 "Are you calling this script from there ?\n\n" +\
                 "  > cd ${{{0} ROM dir}}\n".format(self.rom()) +\
                 "  > ${{renesas-bsp-rom-writer}}/board/{}/linux/{}-writer".format(self.board(), self.rom()))
        self.ask_yn(quit=True)

    #--------------------
    # confirm_info
    #--------------------
    def confirm_info(self):
        while 1:
            self.__print_info()
            if (self.ask_yn()): break;

            # reset all setting
            # ignore rom here
            if (self.__soc  is not None): self.__soc  = ""
            if (self.__ver  is not None): self.__ver  = ""
            if (self.__tty  is not None): self.__tty  = ""
            if (self.__mac  is not None): self.__mac  = ""
            if (self.__mode is not None): self.__mode = ""
            self.setup()

    #--------------------
    # auto_cmd_is_supported
    #--------------------
    def auto_cmd_is_supported(self):
        if (self.__auto_cmd is None):
            return False
        else:
            return True

    #--------------------
    # auto_cmd
    #--------------------
    def auto_cmd(self, cmd):
        if (self.__auto_cmd is not None):
            return self.run("{} {}".format(self.__auto_cmd, cmd))
        else:
            return False

#====================================
#
# guide
#
#====================================
class guide(base):

    #--------------------
    # __del__
    #--------------------
    def __del__(self):
        self.__log.close()

    #--------------------
    # __init__
    #--------------------
    def __init__(self):
        file_name = "{}/renesas-bsp-rom-writer.log".format(self.cwd())
        self.__log = open(file_name, mode='w')

    #--------------------
    # init
    #--------------------
    def init(self, board):
        # for guide
        self.__serial		= None
        self.__line_array	= []
        self.__remain_lines	= ""
        self.__board		= board

        self.__serial = serial.Serial(
            port	= board.tty(),
            baudrate	= board.baudrate(),
            bytesize	= serial.EIGHTBITS,
            parity	= serial.PARITY_NONE,
            stopbits	= serial.STOPBITS_ONE)

    #--------------------
    # log
    #--------------------
    def log(self, msg):
            self.__log.write(msg)

    #--------------------
    # __load_input
    #--------------------
    def __load_input(self):
        size = self.__serial.inWaiting()
        if (not size): return

        # read serial data
        # and print it immediately
        line = self.__serial.read(size).decode(errors='ignore')
        print(line, end="", flush=True)

        # add new data to end of previous remain data
        self.__remain_lines += line

        #
        # We can't handle expected data in big one-line data,
        # because current "end of arrived data" might be in the middle
        # of the expected data.
        #
        # ex) expected data is "ABCD",
        #     "AB" is arrived, but "CD" is not.
        #
        #	@ : previous loaded data
        #	x : new      loaded data
        #	[]: line break (= \n)
        #
        #	__remain_lines = @@@@@@@@@@@@xxxxxx[]xxxxxAB
        #
        # In this case, we can't find expected data (= ABCD) from
        # __remain_lines, and can't clear __remain_lines because
        # we can't judge the part of expect data was included or not.
        #
        # Keeping __remain_lines and checks it everytime until it
        # could find expected data is very waste of CPU power.
        #
        # Thus it transforms the data to line array,
        # and remain_lines. see __expect()
        #
        #	@@@@@@@@@@@@xxxxxx	-> __line_array
        #	xxxxxxxxxxxxxxxxxx	-> __line_array
        #	xxxx			-> __remain_lines
        #
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
        #
        # ex)
        #	@ : previous loaded data
        #	x : new      loaded data
        #
        #	@@@@@@@@@@@@xxxxxx	: __line_array
        #	xxxxxxxxxxxxxxxxxx	: __line_array
        #	xxxx			: __remain_lines
        #

        #
        # pop older data, and check it line-by-line
        #
        #	@@@@@@@@@@@@xxxxxx	: __line_array
        #	xxxxxxxxxxxxxxxxxx	: __line_array
        #
        while len(self.__line_array) > 0:
            line = self.__line_array.pop(0)
            self.log(line)
            if (pattern in line):
                return True
        #
        # check last data
        #
        #	xxxx			: __remain_lines
        #
        idx = self.__remain_lines.find(pattern)
        if (idx >= 0):
            #
            # remove matched pattern from remain lines
            #
            # ex) pattern = ABCD
            # before __remain_lines : xxxABCDyyyyy
            # after  __remain_lines : yyyyy
            #
            idx += len(pattern)
            self.log(self.__remain_lines[:idx])
            self.__remain_lines = self.__remain_lines[idx:]
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
    # board
    #--------------------
    def board(self):
        return self.__board

    #--------------------
    # expect
    #--------------------
    def expect(self, pattern, timeout=60):
        if (not self.___expect(pattern, timeout)):
            self.error("expect timeout")

    #--------------------
    # send
    # send_file
    #--------------------
    def send(self, cmd="", end="\r"):
        return self.__serial.write("{}{}".format(cmd, end).encode())
    def send_file(self, file):
        self.log("\n[send {}]\n".format(file))
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
    # print_msg_power
    #--------------------
    def print_msg_power(self, onoff):
        self.msg("Power {}".format(onoff))

    #--------------------
    # ask_loop
    #--------------------
    def ask_loop(self):
        list = ["Update all files without asking",
                "Ask one by one whether to update"]
        return list.index(self.select("You can select update style", list))

    #--------------------
    # skip_run
    #--------------------
    def skip_run(self, map, ask):
        if ("ignore" == self.board().config_read(map["srec"])):
            self.msg("config file indicates ignore {}".format(map["srec"]))
            return True

        if (ask):
            self.msg("Do you update this ?\n" +\
                     map["srec"] + " (" + map["addr"] + " : " + map["save"] + ")")
            if (not self.ask_yn()):
                return True

    #--------------------
    # sk_type_send
    #--------------------
    def sk_type_main_loop(self, select, yes_loop, ask):

        for map in self.board().addr_map("addr_map"):
            if (self.skip_run(map, ask)):
                continue

            self.send()
            self.expect(">")

            self.send("xls2")

            self.expect("Select (1-3)>")
            self.send(select)

            for i in range(yes_loop):
                self.expect("(Push Y key)")
                self.send("Y", end="")

            self.expect("Please Input : H'")
            self.send(map["addr"])

            self.expect("Please Input : H'")
            self.send(map["save"])

            self.expect("please send !")
            self.send_file("{}/{}".format(self.cwd(), map["srec"]))

            self.expect("Clear OK?(y/n)")
            self.send("y", end="")

            self.expect(">")

    #--------------------
    # wh_type_emmc_loop
    #--------------------
    def wh_type_emmc_loop(self, select, yes_loop, ask):

        for map in self.board().addr_map("emmc_map"):
            if (self.skip_run(map, ask)):
                continue

            self.send()
            self.expect(">")

            self.send("em_w")

            for i in range(yes_loop):
                self.expect("(Push Y key)")
                self.send("Y", end="")

            self.expect("Select area(0-2)>")
            self.send(select)

            self.expect("Please Input Start Address in sector :")
            self.send(map["save"])

            self.expect("Please Input Program Start Address :")
            self.send(map["addr"])

            self.expect("please send !")
            self.send_file("{}/{}".format(self.cwd(), map["srec"]))

            self.expect("EM_W Complete!")

    #--------------------
    # iron_type_main_loop
    #--------------------
    def iron_type_main_loop(self, ask, map, cmd):

        for map in self.board().addr_map(map):
            if (self.skip_run(map, ask)):
                continue

            time.sleep(0.2)
            self.send()

            self.expect(" N:>")
            time.sleep(0.2)
            self.send(cmd)

            self.expect(" N:  Input data : 0x")
            time.sleep(0.4)
            self.send(map["addr"])

            self.expect(" N:  Input data : 0x")
            time.sleep(0.4)
            self.send(map["save"])

            self.expect("please send ! (Motorola S-record)")
            time.sleep(0.4)
            self.send_file("{}/{}".format(self.cwd(), map["srec"]))

            self.expect(" N:Command success.")
