#!/bin/bash


printf "/*****************************************************************************************\n"
printf " * IMPORTANT\n"
printf " * DO NOT EDIT THIS FILE\n"
printf " * IT IS AUTO GENERATED FROM shared/fordringsgruppe.js\n"
printf " * And will be overwritten by makefile\n"
printf " * \n"
printf " * It is generated by the script makefile-utils/gen_fordringsgruppe_frontend.sh\n"
printf " *****************************************************************************************/\n"
printf "let groups = "
cat $1
printf "\nexport {groups};\n"
