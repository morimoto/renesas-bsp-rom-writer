all: AArch32_Flash_writer_SCIF_DUMMY_CERT_E6300400_ULCB.mot loop_yocto

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
loop_yocto:
	@CMD=loop_soc LIST="$(shell ls yocto)" make -s loop
loop_soc:
	@ver=${param} CMD=convert_cmd  LIST="$(shell ls yocto/${param})" make -s loop
convert_cmd:
	ver=${ver} soc=${param} make -s linux/${param}_${ver}
linux/${soc}_${ver}: yocto/${ver}/${soc}
	@echo "create $@"
	script/converter $^ > $@

#--------------------------
#
# for create mot
#
#--------------------------
AArch32_Flash_writer_SCIF_DUMMY_CERT_E6300400_ULCB.mot: flash_writer/AArch32_output/AArch32_Flash_writer_SCIF_DUMMY_CERT_E6300400_ULCB.mot
	mv     flash_writer/AArch32_output/AArch32_Flash_writer_SCIF_DUMMY_CERT_E6300400_ULCB.mot .
	rm -fr flash_writer/AArch32_output/

flash_writer/AArch32_output/AArch32_Flash_writer_SCIF_DUMMY_CERT_E6300400_ULCB.mot: flash_writer/gcc-linaro-7.3.1-2018.05-x86_64_arm-eabi/bin/arm-eabi-gcc
	cd flash_writer;\
	git pull;\
	CROSS_COMPILE=./gcc-linaro-7.3.1-2018.05-x86_64_arm-eabi/bin/arm-eabi- make AArch=32 BOARD=ULCB

flash_writer/gcc-linaro-7.3.1-2018.05-x86_64_arm-eabi/bin/arm-eabi-gcc: flash_writer/gcc-linaro-7.3.1-2018.05-x86_64_arm-eabi.tar.xz
	cd flash_writer;\
	tar xvf gcc-linaro-7.3.1-2018.05-x86_64_arm-eabi.tar.xz
	touch $@

flash_writer/gcc-linaro-7.3.1-2018.05-x86_64_arm-eabi.tar.xz:
	git clone https://github.com/renesas-rcar/flash_writer.git;\
	cd flash_writer;\
	wget https://releases.linaro.org/components/toolchain/binaries/7.3-2018.05/arm-eabi/gcc-linaro-7.3.1-2018.05-x86_64_arm-eabi.tar.xz


