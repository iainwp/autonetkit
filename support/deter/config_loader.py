'''
Checking lab.conf file being passed to openstack.py
Populating Net and IP lists based off information in lab.conf
@Author: Myles Grindon
Heavily modified for deter - mostly removing stuff
@Author: Iain Phillips
'''

import sys
import os
import ConfigParser

class Cfnode:
  def __init__(self, n):
    self.name = n
    self.interfaces = []

  def addif(self, name, addr, cd):
    self.interfaces.append([name,addr,cd])

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
        [addr,cd] = x.split(",")
        if host not in self.nai:
          self.nai[host] = Cfnode(host)
        self.nai[host].addif(inf, addr, cd)
      
    
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
