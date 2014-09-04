#!/usr/bin/python

import re
import subprocess
import sys


def addr_to_name(find_addrs, ifconfig='/sbin/ifconfig'):
    '''
    Take a list of IP addresses and return a dict mapping each address to an
    interface name.  Invalid IP addresses are ignored.

    Args: 
	find_addrs is a list of IP addresses.  If it is empty, return a dict
	with all the valid IPs and the interface to which they are assigned.

	ifconfig is an optional string that gives the path to an ifconfig
	command.  Shouldn't be needed.

    Returns the dict containing all the IP addressed found as keys and the
    interface name as values.  If an IP is found twice, the last one found is
    returned.
    '''
    p = subprocess.Popen([ifconfig], stdout=subprocess.PIPE)
    rv = { }


    valid_ip_string = '\d+\\.\d+\\.\d+\\.\d+'
    valid_ip_re = re.compile(valid_ip_string + '$')
    dot_re = re.compile('\\.')

    ips = []

    # Validate IPs and put them into ips as valid regular expressions -
    # with the .'s escaped.

    for ip in find_addrs:
	if valid_ip_re.match(ip) is None:
	    continue
	ips.append(dot_re.sub('\\.', ip))

    # Nothing to look for? find 'em all
    if len(ips) == 0:
	ips = [ valid_ip_string ]

    name_re = re.compile('^(\w+):?')
    # Build a regular expression that matches all the IPs.  We'll call ifconfig
    # once and look for all the IPs.
    addr_re= re.compile('inet(\s+addr:)?\s*(%s)' % '|'.join(ips))
    print addr_re.pattern

    for l in p.stdout:
	# First match finds the name of the current interface
	m = name_re.match(l)
	if m is not None:
	    ifname = m.group(1)
	    continue
	# Second match finds IP address of current interface.  addr_re matches
	# if it's an IP we're looking for.
	m = addr_re.search(l)
	if m is not None:
	    rv[m.group(2)] = ifname
    return rv

# Command line
rv = addr_to_name(sys.argv[1:])
for (k, v) in rv.items():
    print '%s: %s' % (k, v)
