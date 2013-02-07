"""
"""

from django.utils import unittest
from django.utils.timezone import now
from django.core import management

from referentiel.models import Host, Service, Status, Reference, Supervisor
from sendim.models import Alert, Event
from sendim.tests.defs import create_event, create_alert, internet_is_on

from datetime import datetime, timedelta

class Graph_TestCase(unittest.TestCase):
    """
    Test communicaton with metrology.
    """
    def setUp(self):
        management.call_command('loaddata', 'test_supervisor.json', database='default', verbosity=0)

    def tearDown(self):
        Alert.objects.all().delete()
        Event.objects.all().delete()

    @unittest.skipIf(not internet_is_on(), 'No internet connection available.')
    def test_RRDTool(self):
        """
        Test to get a list of graph from nagios.demo.netways.de
        for host 'c1-activedirectory' and service 'win-mem+virtual'.
        """
        # Trouver les host supervise sur http://nagios.demo.netways.de/nagios/cgi-bin/status.cgi
        management.call_command('loaddata', 'test_rrdtool_host.json', database='default', verbosity=0)
        GRAPH_LIST_URL = 'https://nagios.demo.netways.de/pnp4nagios/graph?host=c1-activedirectory-1&srv=win-mem+virtual&view=0'
        GRAPH_URL = 'https://nagios.demo.netways.de/pnp4nagios/image?host=c1-activedirectory-1&srv=win-mem+virtual&view=0'
        S = Supervisor.objects.get(name__icontains='Netways')
        opener = S.getOpener()
        A = create_alert(service='win-mem virtual')
       
        # Find graphs
        ## Test to get a graph list URL
        graph_list_url = S.get_graph_url(alert=A, prefix='graph')
        self.assertEqual(GRAPH_LIST_URL, graph_list_url)

        ## Test to open this URL
        response = opener.open(graph_list_url)
        info = response.info()
        self.assertEqual(200,response.getcode())
        self.assertIn('text/html', info['content-type'])

        # Get graph
        ## Test to get a graph URL
        graph_url = S.get_graph_url(alert=A)
        self.assertEqual(GRAPH_URL, graph_url)

        ## Test to open this URL
        response = opener.open(graph_url)
        info = response.info()
        self.assertEqual(200,response.getcode())
        self.assertIn('image/png', info['content-type'])

    @unittest.skipIf(not internet_is_on(), 'No internet connection available.')
    def test_N2RDD(self):
        """                                                                                          
        Test to get a list of graph from sysnetmon.diglinks.com
        for host 'core.diglinks.com' and service '02_load'.
        """
        # Trouver les host supervise sur http://nagios.demo.netways.de/nagios/cgi-bin/status.cgi     
        management.call_command('loaddata', 'test_n2rrd_host.json', database='default', verbosity=0)
        GRAPH_LIST_URL = 'http://sysnetmon.diglinks.com/cgi-bin/rrd2graph.cgi?hostname=core.diglinks.com&service=02_load'
        GRAPH_URL = 'http://sysnetmon.diglinks.com/cgi-bin/n2rrd_images_cache/core.diglinks.com/core.diglinks.com_load_Daily.png'
        S = Supervisor.objects.get(name__icontains='SysNetmon')                                      
        opener = S.getOpener()
        A = create_alert(host='core.diglinks.com', service='02_load')                                                          
        
        # Find graphs
        graph_list_url = S.get_graph_url(alert=A, prefix='graph')                                    
        self.assertEqual(GRAPH_LIST_URL, graph_list_url)                                             
        handle = opener.open(graph_list_url)                                                         
        
        # TO FINISH
        # Get graph 
        #graph_url = S.get_graph_url(alert=A)
        #self.assertEqual(GRAPH_URL, graph_url)                                            
        #handle = opener.open(graph_url)
