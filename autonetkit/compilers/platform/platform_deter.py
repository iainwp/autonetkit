"""Compiler for Deter"""
import os
import autonetkit
import autonetkit.config
import autonetkit.log as log
import autonetkit.plugins.naming as naming
from autonetkit.compilers.platform.platform_base import PlatformCompiler
import string
import itertools
from autonetkit.ank_utils import alphabetical_sort as alpha_sort
from autonetkit.compilers.device.quagga import QuaggaCompiler
from autonetkit.nidb import ConfigStanza

class DeterCompiler(PlatformCompiler):
    """OpenStack Platform Compiler"""
    @staticmethod
    def index_to_int_id(index):
        """Maps interface index to ethx e.g. eth1, eth2, ... Due to Mgmt network"""
        return "eth%s" % str(int(index)+1)

    def compile(self):
        log.info("Compiling Deter for %s" % self.host)
        g_phy = self.anm['phy']
        quagga_compiler = QuaggaCompiler(self.nidb, self.anm)
# TODO: this should be all l3 devices not just routers
        for phy_node in g_phy.l3devices(host=self.host, syntax='quagga'):
            folder_name = naming.network_hostname(phy_node)
            DmNode = self.nidb.node(phy_node)
            DmNode.add_stanza("render")
            #TODO: order by folder and file template src/dst
            DmNode.render.base = os.path.join("templates","quagga_deter")
            DmNode.render.template = os.path.join("templates",
                "deter_startup.mako")
            DmNode.render.dst_folder = os.path.join("rendered",
                self.host, "deter")
            DmNode.render.base_dst_folder = os.path.join("rendered",
                self.host, "deter", folder_name)
            DmNode.render.dst_file = "%s.startup" % folder_name

            DmNode.render.custom = {
                    'abc': 'def.txt'
                    }

# allocate zebra information
            DmNode.add_stanza("quagga")
            if DmNode.is_router():
                DmNode.quagga.password = "1234"
            hostname = folder_name
            if hostname[0] in string.digits:
                hostname = "r" + hostname
            DmNode.hostname = hostname  # can't have . in quagga hostnames
            #DmNode.add_stanza("ssh")
            #DmNode.ssh.use_key = True  # TODO: make this set based on presence of key

            # Note this could take external data
            int_ids = itertools.count(0)
            for interface in DmNode.physical_interfaces():
                numeric_id = int_ids.next()
                interface.numeric_id = numeric_id
                interface.id = self.index_to_int_id(numeric_id)

# and allocate tap interface
            #DmNode.add_stanza("tap")
            #DmNode.tap.id = self.index_to_int_id(int_ids.next())

            quagga_compiler.compile(DmNode)

            if DmNode.bgp:
                DmNode.bgp.debug = True
                static_routes = []
                DmNode.quagga.static_routes = static_routes
	
        # and lab.conf
        #self.allocate_tap_ips()
        self.lab_topology()

    ''' NOT USED'''
    def allocate_tap_ips(self):
        """Allocates TAP IPs"""
        settings = autonetkit.config.settings
        lab_topology = self.nidb.topology(self.host)
        from netaddr import IPNetwork
        address_block = IPNetwork(settings.get("tapsn")
            or "172.16.0.0/16").iter_hosts() # added for backwards compatibility
        lab_topology.tap_host = address_block.next()
        lab_topology.tap_vm = address_block.next()  # for tunnel host
        for node in sorted(self.nidb.l3devices(host=self.host)):
            node.tap.ip = address_block.next()

    def lab_topology(self):
# TODO: replace name/label and use attribute from subgraph
        lab_topology = self.nidb.topology(self.host)
        lab_topology.render_template = os.path.join("templates",
            "deter_lab_conf.mako")
        lab_topology.render_dst_folder = os.path.join("rendered",
            self.host, "deter")
        lab_topology.render_dst_file = "lab.conf"
        lab_topology.description = "AutoNetkit Lab"
        lab_topology.author = "AutoNetkit"
        lab_topology.web = "www.autonetkit.org"
        host_nodes = list(
            self.nidb.nodes(host=self.host, platform="deter"))
        if not len(host_nodes):
            log.debug("No Deter hosts for %s" % self.host)
# also need collision domains for this host
        cd_nodes = self.nidb.nodes("broadcast_domain", host=self.host)
        host_nodes += cd_nodes
        subgraph = self.nidb.subgraph(host_nodes, self.host)

        lab_topology.machines = " ".join(alpha_sort(naming.network_hostname(phy_node)
            for phy_node in subgraph.l3devices()))

        lab_topology.config_items = []
        for node in sorted(subgraph.l3devices()):
	    	ip_version = node.ip.use_ipv4
		collision_domains = ""; ip_addresses = ""; 		 
	    
		for interface in node.physical_interfaces():
			#log.info(node.physical_interfaces())
                	broadcast_domain = interface.ipv4_subnet
			ip_address = interface.ipv4_address
                	numeric_id = interface.numeric_id
                
			# Handling Commas in the configuration
			if numeric_id > 0:
			    collision_domains += ", " + str(broadcast_domain)
			    ip_addresses += ", " +  str(ip_address)
			else:
			    collision_domains += str(broadcast_domain)
			    ip_addresses += str(ip_address)
		    
		# One stanza per node to make import easy
		stanza = ConfigStanza(
            		device=naming.network_hostname(node),
                   	#key=numeric_id,
                   	value=collision_domains,
	    		ipaddr=ip_addresses
               	); 
		lab_topology.config_items.append(stanza); 

        #lab_topology.tap_ips = []
        #for node in subgraph:
            #if node.tap:
                #stanza = ConfigStanza(
                    #device=naming.network_hostname(node),
                    #id=node.tap.id.replace("eth", ""),  # strip ethx -> x
                    #ip=node.tap.ip,
                #)
                #lab_topology.tap_ips.append(stanza)

        #lab_topology.tap_ips = sorted(lab_topology.tap_ips, key = lambda x: x.ip)
        lab_topology.config_items = sorted(lab_topology.config_items, key = lambda x: x.device)
