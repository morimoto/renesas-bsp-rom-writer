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
    __top = os.path.abspath(os.path.dirname(__file__) + "../../")
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
        return self.runl(f'grep -w "^{tag}" {file} | sed -e "s/^{tag}: *\\"//g" | sed -e "s/\\"$//g"')

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
            text += f"\n  {i + 1}) " + list[i]

        while 1:
            self.msg(text)
            try:
                ret = int(self.input(f"select number (1-{max}): "))
            except KeyboardInterrupt:
                sys.exit(1)
            except ValueError:
                ret = -1
            if (ret <= 0 or ret > max):
                self.error(f"select number in 1 - {max}", quit=0)
            else:
                return list[ret - 1]

    #--------------------
    # ask_yn
    #--------------------
    def ask_yn(self, quit=None, default=None):
        while 1:
            msg = f" <default {default}>: " if (default) else ": "
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
            print(f"* {txt}")
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
            print(f"| {txt:<{l}} |")

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
    def __init__(self, board):

        file = board.dir_info("switch")

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
            if (os.path.exists(f"{b.cwd()}/{am[1]}")):
                addr = b.run(f"head -n 2 {b.cwd()}/{am[1]} | grep S3 | head -n 1 | cut -c5-12")
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
    def init(self, baudrate=115200, board_name=None, auto_cmd=None):

        # None   : not use
        # ""     : be used, but not yet selected
        # "xxx"  : be used, and selected
        if (board_name):
            self.__board_name = board_name
        else:
            self.__board_name = os.path.splitext(os.path.basename(sys.argv[0]))[0]
        self.__baudrate	= baudrate

        # for inside
        self.__config	= f"renesas_bsp_rom_writer.{self.__board_name}"
        self.__addr_map	= {}
        self.__map	= None
        self.__tty	= ""
        self.__title	= None

        # for auto command
        self.__auto_cmd = auto_cmd	# path from ${TOP}/board/
        self.__auto_cmd_tty = None	# None:		not used
                                  	# /dev/ttyXX:	use specified serial

        self.confirm_location()
        self.config_load()
        self.setup()

        self.confirm_info()
        self.config_save()

    #--------------------
    # mot_file
    #--------------------
    def mot_file(self):
        return "{}/{}".format(self.cwd(),
                              self.ttm_array(self.map(), "mot_file")[0])

    #--------------------
    # mode_explanation
    #--------------------
    def mode_explanation(self): return ""

    #--------------------
    # tty
    # baudrate
    #--------------------
    def tty(self):	return self.__tty
    def map(self):	return self.__map
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
    # dir_xxx
    #--------------------
    def dir_board(self, path=""):
        return f"{self.top()}/board/{self.__board_name}/{path}"
    def dir_info(self, path=""):	return self.dir_board("info/" + path)

    #--------------------
    # config_xxx
    #--------------------
    def config_file(self):
        return f"{self.cwd()}/{self.__config}"

    def config_read(self, tag):
        return self.run(rf'grep "^\[{tag}\]:" {self.config_file()} 2>/dev/null | cut -d : -f 2-')

    def config_write(self, tag, data):
        tmp = f"/tmp/renesas-bsp-rom-writer-config-{os.getpid()}"
        if (os.path.exists(self.config_file())):
            self.run(rf'grep -v "^\[{tag}\]:" {self.config_file()} > {tmp}')
        self.run(f"echo \"[{tag}]:{data}\" >> {tmp}")
        self.run(f"mv -f {tmp} {self.config_file()}")
        if (not os.path.exists(self.config_file())):
            self.error("cann't save configs")

    def config_load(self):
        # __init__() set default value
        # load config if value was ""
        if (self.__tty  == ""): self.__tty  = self.config_read("tty")

        # The auto_cmd is specific to each board
        if (self.__auto_cmd is not None):
            self.__auto_cmd_tty = self.config_read("auto_cmd_tty")
            if (self.__auto_cmd_tty == ""):
                self.__auto_cmd_tty = None
            else:
                if (self.__tty_error(self.__auto_cmd_tty)):
                    self.error(f"[auto_cmd_tty](= {self.__auto_cmd_tty}) is not valid tty\n")

    def config_save(self):
        if (self.__tty  is not None): self.config_write("tty",     self.__tty)

    #--------------------
    # setup
    #
    # overwrite select_xx() on each board
    # if default select_xx() was not good match
    #--------------------
    def setup(self):
        self.detect_map()
        self.select_tty()

    #--------------------
    # detect_map
    #--------------------
    def detect_map(self):
        map_files = self.runl("ls ./*.map 2>/dev/null")
        map_files.extend(self.runl(f"ls {self.dir_info()}map/*.map"))

        for map_file in map_files:
            title = self.ttm_array(map_file, "title")[0]
            mot   = self.ttm_array(map_file, "mot_file")[0]
            addr_map = {}

            if (not os.path.exists(mot)):
                continue

            for key in ["addr_map", "emmc_map", "ufs_map"]:
                map = config_map(map_file, key)
                if (not map.len()):
                    continue
                addr_map[key] = map
                for val in map:
                    if (not os.path.exists(val["srec"])):
                        addr_map = {}
                        break
                if (not len(addr_map)):
                    break
            if (len(addr_map)):
                if ("ignore" == self.config_read("confirm_map")):
                    self.msg("config file indicates ignore map confirmation\n" +
                            f"    [{title}]    ")
                    accept = True
                else:
                    self.msg("It detected\n" +
                            f"    [{title}]    \n" +
                             "Is this your expected ?")
                    accept = self.ask_yn()
                if (accept):
                    self.__map		= map_file
                    self.__addr_map	= addr_map
                    self.__title	= title
                    return

        self.error("No ROM map found", 1)

    #--------------------
    # select_tty (default)
    #--------------------
    def tty_connection(self):
        return self.ttm_array(self.dir_info("switch"), "tty_connection")[0]

    def __tty_error(self, tty):
        if (not os.path.exists(tty)):
            return 1

        m1 = re.match("/dev/tty.*",     tty)
        m2 = re.match("/dev/serial/.*", tty)
        if (not m1 and not m2):
            return 1

        if (not os.access(tty, os.R_OK) or
            not os.access(tty, os.W_OK)):
            self.msg(f"You don't have permission to access to {tty}.\n" +\
                     "It requires root or \"dialout group\" permission, maybe ?\n" +\
                     "Check it\n" \
                    f"   > ls -l {tty}\n\n" +\
                     "Check your joined group\n" \
                     "   > id\n\n" \
                     "Let's join to \"dialout group\"\n" \
                    f"   > sudo gpasswd -a {getpass.getuser()} dialout\n\n" +\
                     "Maybe you need to logout and login again.\n" \
                     "Then, check your joined group.\n" \
                     "   > id\n\n" \
                     "Retry to call this script if all are OK")
            sys.exit(1)
            return 1

    def __tty_owner_info(self):
        fuser = self.run(f"fuser -u {self.__tty} 2>&1")
        if not fuser:
            return None
        pids  = re.findall(r'(\d+)\(',   fuser)
        users = re.findall(r'\(([^)]+)\)', fuser)
        owners = []
        for pid, user in zip(pids, users):
            comm = self.run(f"ps -p {pid} -o comm= 2>/dev/null") or "unknown"
            owners.append(f"{comm} ({user}, pid {pid})")
        return ", ".join(owners) if owners else None

    def __tty_kill_owner(self):
        self.run(f"fuser -k {self.__tty} 2>&1")
        time.sleep(0.5)
        if (self.__tty_owner_info()):
            self.error(f"Failed to kill owner of {self.__tty}\nPlease free it manually", quit=0)
            self.__tty = ""

    def __tty_ask_kill_owner(self):
        owner = self.__tty_owner_info()
        if not owner:
            return
        if ("ignore" == self.config_read("tty_owner")):
            self.__tty_kill_owner()
        else:
            self.msg(f"{owner} is using {self.__tty}\nDo you want to kill it ?")
            if (self.ask_yn()):
                self.__tty_kill_owner()
            else:
                self.__tty = ""

    def select_tty(self):
        if (self.__tty != ""):
            return
        if ("ignore" == self.config_read("select_tty")):
            self.msg("config file indicates ignore tty select")
            self.__tty_ask_kill_owner()
            return

        text = "Your board and PC need to connect\n" + self.tty_connection()
        self.msg(text)
        self.ask_yn(quit=True)

        self.__tty_ask_kill_owner()

        text = "Which tty is connected to board ?\n" +\
               "  ex) /dev/ttyUSBx\n\n" +\
               "You can confirm it by this command maybe ?\n" +\
               "  > dmesg | grep ttyUSB"

        while (self.__tty_error(self.__tty)):
            print("\n")
            self.msg(text)
            self.__tty = self.input("ex) /dev/ttyUSBx: ")
            print()
            if (self.__tty_error(self.__tty)):
                self.error(f"{self.__tty} is not exist or not tty\n" +
                           "Please select like /dev/ttyUSBx", quit=0)
            else:
                self.__tty_ask_kill_owner()

    #--------------------
    # print_info
    #--------------------
    def __print_info(self):
        text = "Your selected settings are...\n\n" + \
              f"  [Board]:   {self.__board_name}\n" +\
              f"  [Title]:   {self.__title}\n" +\
              f"  [TTY]:     {self.__tty} ({self.baudrate()})\n"

        if (self.__auto_cmd_tty is not None):
            text += f"  [Auto command]:     {self.__auto_cmd}\n"
            text += f"  [Auto command TTY]: {self.__auto_cmd_tty}\n"

        text += "\nYou can manually setup if you want\n" +\
               f"   > vi ./{self.__config}\n"

        for name in self.addr_map().keys():
            text += f"\n[{name}]\n"
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

        self.msg("This script requires be called from your ROM directory.\n" +\
                 "Are you calling this script from there ?\n\n" +\
                 "  > cd ${your ROM dir}\n" +\
                f"  > ${{renesas-bsp-rom-writer}}/board/{self.__board_name}/linux/rom-writer")

        self.ask_yn(quit=True)

    #--------------------
    # confirm_info
    #--------------------
    def confirm_info(self):
        while 1:
            self.__print_info()
            if ("ignore" == self.config_read("confirm_info")):
                self.msg("config file indicates ignore info confirmation")
                break
            if (self.ask_yn()): break;

            # reset all setting
            # ignore rom here
            self.__tty		= ""
            self.__addr_map	= {}
            self.__map		= None

            self.setup()

    #--------------------
    # auto_cmd_is_available
    #--------------------
    def auto_cmd_is_available(self):
        if (self.__auto_cmd_tty is None):
            return False
        else:
            return True

    #--------------------
    # auto_cmd
    #--------------------
    def auto_cmd(self, cmd):
        if (self.__auto_cmd_tty is not None):
            return self.run(f"{self.top()}/board/{self.__auto_cmd} {self.__auto_cmd_tty} {cmd}")
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
        file_name = f"{self.cwd()}/renesas-bsp-rom-writer.log"
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
        self.__sw		= switch(board)

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
    # sw
    #--------------------
    def sw(self):
        return self.__sw

    #--------------------
    # expect
    #--------------------
    def expect(self, pattern, timeout=60):
        if (not self.___expect(pattern, timeout)):
            self.error("expect timeout")

    #--------------------
    # send
    # send_file
    # send_mot_file
    #--------------------
    def send(self, cmd="", end="\r"):
        return self.__serial.write(f"{cmd}{end}".encode())
    def send_file(self, file):
        self.log(f"\n[send {file}]\n")
        self.msg("Now it is sending below file to board.\n"\
                 "Please wait.\n"\
                f"[{os.path.basename(file)}]")
        with open(file, "rb") as f:
            self.__serial.write(f.read())
        self.send("\n", end="")
    def send_mot_file(self):
        self.send_file(self.board().mot_file())

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
        self.msg(f"Power {onoff}")

    #--------------------
    # ask_loop
    #--------------------
    def ask_loop(self):
        list = ["Update all files without asking",
                "Ask one by one whether to update"]
        if ("all" == self.board().config_read("update_style")):
            self.msg("config file indicates update all files without asking")
            return 0
        elif ("ask" == self.board().config_read("update_style")):
            self.msg("config file indicates ask one by one whether to update")
            return 1
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

            self.expect("N:>")
            time.sleep(0.2)
            self.send(cmd)

            self.expect("N:  Input data : 0x")
            time.sleep(0.4)
            self.send(map["addr"])

            self.expect("N:  Input data : 0x")
            time.sleep(0.4)
            self.send(map["save"])

            self.expect("please send ! (Motorola S-record)")
            time.sleep(0.4)
            self.send_file("{}/{}".format(self.cwd(), map["srec"]))

            self.expect("N:Command success.")
