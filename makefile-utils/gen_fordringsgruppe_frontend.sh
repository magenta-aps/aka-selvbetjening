#!/bin/bash


printf "/*****************************************************************************************\n"
printf " * IMPORTANT\n"
printf " * DO NOT EDIT THIS FILE\n"
printf " * IT IS AUTO GENERATED FROM shared/fordringsgruppe.json\n"
printf " * And will be overwritten by makefile\n"
printf " * \n"
printf " * It is generated by the script makefile-utils/gen_fordringsgruppe_frontend.sh\n"
printf " *****************************************************************************************/\n"
printf "let groups = "
cat $1 | sed 's/"\([^"]*\)" *:/\1:/g'
printf "\nexport {groups};\n"
