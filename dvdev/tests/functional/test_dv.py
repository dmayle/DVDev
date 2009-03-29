from dvdev.tests import *

class TestDvController(TestController):

    def test_index(self):
        response = self.app.get(url(controller='dv', action='index'))
        # Test response...
