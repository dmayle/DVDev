from dvdev.tests import *

class TestMercurialcontrollerController(TestController):

    def test_index(self):
        response = self.app.get(url(controller='mercurialcontroller', action='index'))
        # Test response...
