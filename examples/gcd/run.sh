#!/bin/bash

# Trick to get this script's directory and add it to scpath so that we can run
# this file from project root.
# https://stackoverflow.com/a/246128
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

sc -design gcd \
   gcd.v \
   gcd.sdc \
   -target "freepdk45_demo" \
   -constraint_outline "(0,0)" \
   -constraint_outline "(100.13,100.8)" \
   -constraint_corearea "(10.07,11.2)" \
   -constraint_corearea "(90.25,91)" \
   -loglevel "INFO" \
   -novercheck \
   -quiet \
   -relax \
   -track \
   -clean \
   -scpath $SCRIPT_DIR
