from dvdev.tests import *

class TestOpeniduserController(TestController):

    def test_index(self):
        response = self.app.get(url(controller='openiduser', action='index'))
        # Test response...
