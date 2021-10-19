all: loop_android loop_yocto

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
	../../starterkit/linux/script/converter $^ > $@
