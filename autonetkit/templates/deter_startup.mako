#!/bin/sh
apt-get install quagga
sysctl -w net.ipv4.ip_forward=1
sysctl -w net.ipv6.conf.all.forwarding=1
route del default
/sbin/ifconfig lo 127.0.0.1 up
/etc/init.d/ssh start
/etc/init.d/hostname restart
% if node.zebra:
/etc/init.d/quagga restart
% endif
