from basic_alert import Basic_Alert_TestCase
from host_alert import SingleHost_SingleAlert_TestCase, SingleHost_MultipleAlert_TestCase
from service_alert import SingleService_SingleAlert_TestCase, SingleService_MultipleAlert_TestCase, MultipleService_MultipleAlert_TestCase 
from both_alert import Host_and_service, Service_and_host
from event import Event_TestCase
from supervisor import Supervisor_TestCase
from black_reference import Black_reference_TestCase
from reference import Reference_TestCase
from translation import Translation_TestCase
from client import Login_TestCase, Customer_Client_TestCase
from views import Views_TestCase
from views_configuration import Views_Configuration_TestCase
from webservices import Webservice_TestCase
from glpi_manager import GLPI_Manager_TestCase
from graph import Graph_TestCase
from commands import Commands_TestCase

def suite():
    import doctest
    import unittest
    import defs
    #import glpi_test_server
    TEST_CASES = (
     'sendim.tests.basic_alert',
     'sendim.tests.service_alert',
     'sendim.tests.host_alert',
     'sendim.tests.both_alert',
     'sendim.tests.event',
     'sendim.tests.supervisor',
     'sendim.tests.black_reference',
     'sendim.tests.reference',
     'sendim.tests.translation',
     'sendim.tests.client',
     'sendim.tests.views',
     'sendim.tests.views_configuration',
     'sendim.tests.webservices',
     'sendim.tests.glpi_manager',
     'sendim.tests.graph',
     'sendim.tests.commands'
    )
    suite = unittest.TestSuite()

    suite.addTest(doctest.DocTestSuite(defs))
    for t in TEST_CASES :
        suite.addTest(unittest.TestLoader().loadTestsFromModule(__import__(t, globals(), locals(), fromlist=["*"])))
    return suite
