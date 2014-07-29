#!/usr/bin/env python

'''
Handles the exported configuration files from AutoNetkit for deploying to deter
Usage: 	gendeter.py /path/to/lab.conf /path/to/detertop.xml
@Author: Iain Phillips - modified code from Myles Grindon
'''

import os, sys, time
from deter import topdl
import lxml.etree as etree

from config_loader import ConfigLoader

#
# Handle Configuration File, Check Quota Limits & Prompt If user
# wishes to build environment
# 

def usage():
  print "Usage deter.py /path/to/lab.conf [/path/to/detertop.xml]"

# 0. Check arguments
if len(sys.argv) < 2 or len(sys.argv) > 3:
  usage()
  sys.exit()

if len(sys.argv) >= 2:
  lab_config_file=sys.argv[1]

xml_outputfile = lab_config_file+".xml"
if len(sys.argv) >= 3:
  xml_output_file=sys.argv[2]


# 1. Check config file 
lab_config = ConfigLoader(lab_config_file)

nai = lab_config.getNodesAndInterfaces()

subs=[ topdl.Substrate(name="net"+str(x)) for x in lab_config.getNetworks() ]
elems = []
for h in nai:
  elems.append(topdl.Computer(name=h, 
                              interface=[topdl.Interface(name=i[0], substrate="net"+i[2]) 
                                         for i in nai[h].interfaces]))




top = topdl.Topology(substrates=subs, elements=elems)
print etree.tostring(etree.fromstring(
  topdl.topology_to_xml(top, top='experiment')), pretty_print=True)

#print topdl.topology_to_xml(top, top='experiment')
