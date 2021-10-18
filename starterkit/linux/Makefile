all: script/flash_writer/AArch32_output/AArch32_Flash_writer_SCIF_DUMMY_CERT_E6300400_ULCB.mot loop_yocto loop_android

#--------------------------
# common loop
#--------------------------
loop:
	@for list in ${LIST}; \
	do\
		param="$${list}" make $${CMD};\
	done;

#--------------------------
#
# for convert TeraTarm settings to Tcl
#
#--------------------------
loop_android:
	@CMD=loop_soc target=android LIST="$(shell ls ../android)" make -s loop
loop_yocto:
	@CMD=loop_soc target=yocto LIST="$(shell ls ../yocto)" make -s loop
loop_soc:
	@ver=${param} CMD=convert_cmd  LIST="$(shell ls ../${target}/${param})" make -s loop
convert_cmd:
	ver=${ver} soc=${param} make -s script/${target}/${ver}/${param}
script/${target}/${ver}/${soc}: ../${target}/${ver}/${soc}
	@echo "create $@"
	mkdir -p script/${target}/${ver}
	script/converter $^ > $@

#--------------------------
#
# for create mot
#
#--------------------------
script/flash_writer/AArch32_output/AArch32_Flash_writer_SCIF_DUMMY_CERT_E6300400_ULCB.mot: script/flash_writer/gcc-linaro-7.3.1-2018.05-x86_64_arm-eabi/bin/arm-eabi-gcc
	cd script/flash_writer;\
	CROSS_COMPILE=./gcc-linaro-7.3.1-2018.05-x86_64_arm-eabi/bin/arm-eabi- make AArch=32 BOARD=ULCB

script/flash_writer/gcc-linaro-7.3.1-2018.05-x86_64_arm-eabi/bin/arm-eabi-gcc:
	git clone https://github.com/renesas-rcar/flash_writer.git script/flash_writer;\
	cd script/flash_writer;\
	wget https://releases.linaro.org/components/toolchain/binaries/7.3-2018.05/arm-eabi/gcc-linaro-7.3.1-2018.05-x86_64_arm-eabi.tar.xz; \
	tar xvf gcc-linaro-7.3.1-2018.05-x86_64_arm-eabi.tar.xz
	touch $@
