flash_writer/AArch32_output/AArch32_Flash_writer_SCIF_DUMMY_CERT_E6300400_ULCB.mot: flash_writer/gcc-linaro-7.3.1-2018.05-x86_64_arm-eabi/bin/arm-eabi-gcc
	cd flash_writer;\
	CROSS_COMPILE=./gcc-linaro-7.3.1-2018.05-x86_64_arm-eabi/bin/arm-eabi- make AArch=32 BOARD=ULCB

flash_writer/gcc-linaro-7.3.1-2018.05-x86_64_arm-eabi/bin/arm-eabi-gcc: flash_writer/gcc-linaro-7.3.1-2018.05-x86_64_arm-eabi.tar.xz
	cd flash_writer;\
	tar xvf gcc-linaro-7.3.1-2018.05-x86_64_arm-eabi.tar.xz

flash_writer/gcc-linaro-7.3.1-2018.05-x86_64_arm-eabi.tar.xz:
	git clone https://github.com/renesas-rcar/flash_writer.git;\
	cd flash_writer;\
	wget https://releases.linaro.org/components/toolchain/binaries/7.3-2018.05/arm-eabi/gcc-linaro-7.3.1-2018.05-x86_64_arm-eabi.tar.xz


