GCC=gcc-linaro-7.3.1-2018.05-x86_64_aarch64-elf
GCC_PRE=aarch64-elf
GCC_URL=https://releases.linaro.org/components/toolchain/binaries/7.3-2018.05/aarch64-elf/${GCC}.tar.xz
MOT=script/flash_writer/AArch64_output/AArch64_Flash_writer_SCIF_DUMMY_CERT_E6300400_salvator-x.mot

all: loop_android loop_yocto ${MOT}

clean:
	@rm -fr script/android
	@rm -fr script/yocto

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
	@CMD=loop_soc target=android LIST="$(shell ls ../android | grep map)" make -s loop
loop_yocto:
	@CMD=loop_soc target=yocto LIST="$(shell ls ../yocto | grep map)" make -s loop
loop_soc:
	@map=${param} CMD=convert_cmd  LIST="$(shell ls ../${target}/${param})" make -s loop
convert_cmd:
	soc=${param} make -s script/${target}/${map}/${param}
script/${target}/${map}/${soc}: ../${target}/${map}/${soc}
	@echo "create $@"
	mkdir -p script/${target}/${map}
	./script/converter $^ > $@

#--------------------------
#
# for create mot
#
# StarterKit and Salvator are almost same
# reuse StarterKit.
#--------------------------
${MOT}: script/flash_writer/${GCC}/bin/${GCC_PRE}-gcc
	cd script/flash_writer;\
	CROSS_COMPILE=./${GCC}/bin/${GCC_PRE}- make AArch=64

script/flash_writer/${GCC}/bin/${GCC_PRE}-gcc:
	git clone https://github.com/renesas-rcar/flash_writer.git script/flash_writer;\
	cd script/flash_writer; wget ${GCC_URL}; tar xvf ${GCC}.tar.xz
	touch $@
