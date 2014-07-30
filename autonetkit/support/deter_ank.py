'''
Handles the exported configuration files from AutoNetkit for deploying to deter
Usage: 	gendeter.py /path/to/lab.conf /path/to/detertop.xml
@Author: Iain Phillips - modified code from Myles Grindon
'''

import os, sys, time, tarfile, fnmatch, ConfigParser
import lxml.etree as etree
from deter import topdl

class CfNode:

  class CfInterface:
    def __init__(self, n, a, c, m):
      self.name = n
      self.address = a
      self.cd = c
      self.netmask = m

  def __init__(self, n):
    self.name = n
    self.interfaces = []

  def addif(self, name, addr, cd, mask):
    self.interfaces.append(CfNode.CfInterface(name,addr,cd,mask))

class ConfigLoader:
  
  config_parser   = ConfigParser.ConfigParser()
  config_parser.optionxform = str # Avoids Config parser automatically adjusting node cases (Lower) 
  config_file   = None
  config_dir    = None
  
  nodes_net   = None
  nodes_ip    = None
  nodes_name  = None
  
  quagga_file_list = ['bgpd.conf', 'daemons', 'isisd.conf', 'motd.txt', 'ospfd.conf', 'zebra.conf']
  
  def __init__(self, config_file_path=None):
    self.config_file = config_file_path
    self.checkConfigFile()
    self.checkNodeConfigFiles()
    
    
  def setConfigFile(self, config_file_path):
    self.config_file = config_file_path
    
    
  # Checking
  # 1. File Exists
  # 2. Sections 'Net' & 'IP' are present when read in
  # 3. A Section contains information
  def checkConfigFile(self):
    # 1.
    try:
      if not os.path.isfile(self.config_file):
        sys.stderr.write('Configuration file does not exist!\n')
        sys.exit('Exiting!')
    
    except TypeError:
      sys.stderr.write('Configuration file not provided!\n')
      sys.exit('Exiting!')
      
    # 2. 
    try:
      # NOTE: Input of nodes may be mixed
      # Sorting is *Vital* with rest of code
      self.config_parser.read(self.config_file)
      self.ni = self.config_parser.options("Net")
      self.nodes_net  = set([ n.split(',')[0] for n in self.ni ])
      self.networks = set([self.config_parser.get("Net", n).split(',')[1] for n in self.ni ])
      print self.nodes_net
      print self.networks

      self.nai = {}
      for n in self.ni:
        x = self.config_parser.get("Net", n)
        [host,inf] = n.split(",")
        [addr,cd,mask] = x.split(",")
        if host not in self.nai:
          self.nai[host] = CfNode(host)
        self.nai[host].addif(inf, addr, cd, mask)
      
    
    except ConfigParser.NoSectionError, err:
      sys.stderr.write('Missing configuration section: %s\n' % err)
      sys.exit('Exiting!')
    
    # 3.
    if not self.nodes_net:
      sys.stderr.write('No nodes present in configuration!\n')
      sys.exit('Exiting!')
      
  
  # Checking
  # 1. Number of node.startup files and directories exist (same level as the lab.conf)
  # 2. For each directory there exists the suitable configuration files
  def checkNodeConfigFiles(self):
    self.config_dir = str(os.path.dirname(os.path.realpath(self.config_file)))
    exit = False

    # 1.
    for node in self.nodes_net:
      print "checking ", node 
      # Node startup files
      if not os.path.isfile(self.config_dir + "/" + node + ".startup"):
        print node
        sys.stderr.write('Missing .startup configuration file for node %s!\n' % node)
        sys.exit('Exiting!')
        
      # Node directories
      if not os.path.isdir(self.config_dir + "/" + node):
        sys.stderr.write('Missing configuration directory for node %s!\n' % node)
        exit=True
      
    # 2.
    for node in self.nodes_net:
      node_dir = "/" + node
      print "checking %s/%s" % (self.config_dir,node_dir)
              
      # '/etc' directory
      if not os.path.isdir(self.config_dir+node_dir+"/etc"):
        sys.stderr.write('Missing "/etc" directory for node %s!\n' % node)
        exit=True
          
      # Hostname file
      if not os.path.isfile(self.config_dir+node_dir+"/etc/hostname"):
        sys.stderr.write('Missing "/etc/hostname" file for node %s!\n' % node)
        exit=True
          
      # Zebra directory
      if not os.path.isdir(self.config_dir+node_dir+"/etc/zebra"):
        sys.stderr.write('Missing "/etc/zebra" directory for node %s!\n' % node)
        exit=True
          
      # Quagga files
      for file in self.quagga_file_list:
        if not os.path.isfile(self.config_dir+node_dir+"/etc/zebra/"+str(file)):
          sys.stderr.write('Missing "/etc/zebra/%s" configuration file for node %s\n' % node)
          exit=True

    if exit:
      sys.exit('Exiting!')
  
  # Returning ALL node names

  def getNodesAndInterfaces(self):
    return self.nai
  
  
  def getNetworks(self):
    return self.networks
  


  # Returns the contents of nodes's startup file as a string
  def getNodeStartupFile(self, node_name):
    startup_file_location = str(os.path.realpath(self.config_dir + "/" + node_name + ".startup"))
    startup_file = open(startup_file_location, 'r')
    startup_string = startup_file.read()
    startup_file.close()
    
    return startup_string

#
# Handle Configuration File, Check Quota Limits & Prompt If user
# wishes to build environment
# 

def usage():
  print "Usage deter.py /path/to/lab.conf [/path/to/detertop.xml]"

def main():
  # 0. Check arguments
  if len(sys.argv) < 2 or len(sys.argv) > 3:
    usage()
    sys.exit()

  if len(sys.argv) >= 2:
    lab_config_file=sys.argv[1]

  xml_outputfile = "deter.xml"
  if len(sys.argv) >= 3:
    xml_output_file=sys.argv[2]


  # 1. Check config file 
  lab_config = ConfigLoader(lab_config_file)
  nai = lab_config.getNodesAndInterfaces()

  subs=[ topdl.Substrate(name="net"+str(x)) for x in lab_config.getNetworks() ]
  elems = [topdl.Computer(name=h, 
                          software = topdl.Software(
                            location='file:///proj/bgpsec/tarfiles/'+h+'.tar.gz',
                            install='/'),
                          os = topdl.OperatingSystem(
                            name='Linux', distribution='Ubuntu'),
                          interface=[topdl.Interface(name=i.name, 
                                                     substrate = "net"+i.cd, 
                                                     attribute = [topdl.Attribute('ip4_address', i.address),
                                                                  topdl.Attribute('ip4_netmask', i.netmask),
                                                                  topdl.Attribute('startup','/root/'+h+'.startup')],
                                                   )
                                     for i in nai[h].interfaces])
           for h in nai]
  



  with open(xml_outputfile, "w") as f:
    f.write(etree.tostring(etree.fromstring(
      topdl.topology_to_xml(topdl.Topology(substrates=subs, elements=elems),
                            top='experiment')),
                          pretty_print=True))
    f.close()


  # find folder of lab.conf
  f = os.path.dirname(lab_config_file)
  startups = fnmatch.filter(os.listdir(f), "*.startup")

  for x in startups:
    print x
    r = x.split('.')[0]
    with tarfile.open(os.path.join(r+".tar.gz"),"w:gz") as tar:
      tar.add(os.path.join(f,x),'/root/'+x)
      tar.add(os.path.join(f,r),'/')
      tar.close()
  
  print "Copy the .tar.gz files to /prof/bgpsec/tarfiles on deter"
  print "Copy deter.xml to your homedir on deter"
  print "run containerize.py (check the docs) on the deter.xml file"

if __name__ == "__main__":
  main()
