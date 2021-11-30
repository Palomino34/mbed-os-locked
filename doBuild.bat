@echo off
echo Cleaning....
rd /q /s "__pycache__"
rd /q /s "BUILD"
rd /q /s "codal-mbedos"

REM mbed compile -m NUCLEO_L452RE_P -t GCC_ARM --profile debug
mbed compile -m NUCLEO_L452RE_P -t GCC_ARM --profile release
