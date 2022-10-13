FLASH_WRITER=script/flash_writer
GCC32=gcc-linaro-7.3.1-2018.05-x86_64_arm-eabi
GCC64=gcc-linaro-7.3.1-2018.05-x86_64_aarch64-elf
GCC32_PRE=arm-eabi
GCC64_PRE=aarch64-elf
GCC32_URL=https://releases.linaro.org/components/toolchain/binaries/7.3-2018.05/${GCC32_PRE}/${GCC32}.tar.xz
GCC64_URL=https://releases.linaro.org/components/toolchain/binaries/7.3-2018.05/${GCC64_PRE}/${GCC64}.tar.xz
MOT_STARTERKIT=${FLASH_WRITER}/AArch32_output/AArch32_Flash_writer_SCIF_DUMMY_CERT_E6300400_ULCB.mot
MOT_SALVATOR=${FLASH_WRITER}/AArch64_output/AArch64_Flash_writer_SCIF_DUMMY_CERT_E6300400_salvator-x.mot

all: ${FLASH_WRITER} ${MOT_STARTERKIT} ${MOT_SALVATOR}

# see ${renesas-bsp-rom-writer}/board/gen3-starterkit/config/mot
# why we can't use 64bit gcc on Starterkit
${MOT_STARTERKIT}: script/${GCC32}/bin/${GCC32_PRE}-gcc
	@cd ${FLASH_WRITER};\
	CROSS_COMPILE=../${GCC32}/bin/${GCC32_PRE}- make AArch=32 BOARD=ULCB

${MOT_SALVATOR}: script/${GCC64}/bin/${GCC64_PRE}-gcc
	@cd ${FLASH_WRITER};\
	CROSS_COMPILE=../${GCC64}/bin/${GCC64_PRE}- make AArch=64

script/${GCC32}/bin/${GCC32_PRE}-gcc:
	@cd script; wget ${GCC32_URL}; tar xvf ${GCC32}.tar.xz
script/${GCC64}/bin/${GCC64_PRE}-gcc:
	@cd script; wget ${GCC64_URL}; tar xvf ${GCC64}.tar.xz

${FLASH_WRITER}:
	@git clone https://github.com/renesas-rcar/flash_writer.git ${FLASH_WRITER}
