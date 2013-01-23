from host_alert import *
from service_alert import *
from both_alert import *
from supervisor import *
from reference import *
from translation import *
from client import *
from views import *
from views_configuration import *
from webservices import *

def suite():
    import doctest
    import unittest
    import defs
    TEST_CASES = (
     'sendim.tests.service_alert',
     'sendim.tests.host_alert',
     'sendim.tests.both_alert',
     'sendim.tests.supervisor',
     'sendim.tests.reference',
     'sendim.tests.translation',
     'sendim.tests.webservices',
     'sendim.tests.client',
     'sendim.tests.views'
     'sendim.tests.views_configuration'
    )
    suite = unittest.TestSuite()

    suite.addTest(doctest.DocTestSuite(defs))
    for t in TEST_CASES :
        suite.addTest(unittest.TestLoader().loadTestsFromModule(__import__(t, globals(), locals(), fromlist=["*"])))
    return suite
