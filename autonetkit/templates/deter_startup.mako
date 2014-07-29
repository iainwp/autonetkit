#!/bin/sh
% for i in node.interfaces:
/sbin/ifconfig ${i.id} ${i.ipv4_address} netmask ${i.ipv4_subnet.netmask} broadcast ${i.ipv4_subnet.broadcast} up
% endfor
sysctl -w net.ipv4.ip_forward=1
sysctl -w net.ipv6.conf.all.forwarding=1
route del default
/sbin/ifconfig lo 127.0.0.1 up
/etc/init.d/ssh start
/etc/init.d/hostname restart
% if node.zebra:
/etc/init.d/quagga restart
% endif
