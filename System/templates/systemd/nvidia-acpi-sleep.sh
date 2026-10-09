#!/bin/sh
case "$1" in
    pre)
        echo '\_SB.PCI0.PEG0.PEGP._ON' > /proc/acpi/call
        ;;
    post)
        echo '\_SB.PCI0.PEG0.PEGP._OFF' > /proc/acpi/call
        ;;
esac
