#!/bin/sh
python /proj/bgpsec/python/sub_if.py /root/interfaces.txt /etc/zebra/isisd.conf /etc/zebra/ospfd.conf
dpkg -i --force-confold /proj/bgpsec/packages/quagga_0.99.20.1-0ubuntu0.12.04.3_i386.deb
sysctl -w net.ipv4.ip_forward=1
sysctl -w net.ipv6.conf.all.forwarding=1
