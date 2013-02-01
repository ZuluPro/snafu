from basic_alert import *
from host_alert import *
from service_alert import *
from both_alert import *
from supervisor import *
from black_reference import *
from reference import *
from translation import *
from client import *
from views import *
from views_configuration import *
from webservices import *
from glpi_webservices import *

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
     'sendim.tests.supervisor',
     'sendim.tests.black_reference',
     'sendim.tests.reference',
     'sendim.tests.translation',
     'sendim.tests.client',
     'sendim.tests.views',
     'sendim.tests.views_configuration',
     'sendim.tests.webservices',
     'sendim.tests.glpi_webservices',
    )
    suite = unittest.TestSuite()

    suite.addTest(doctest.DocTestSuite(defs))
    for t in TEST_CASES :
        suite.addTest(unittest.TestLoader().loadTestsFromModule(__import__(t, globals(), locals(), fromlist=["*"])))
    return suite
