from dvdev.tests import *

class TestWikiController(TestController):

    def test_index(self):
        response = self.app.get(url(controller='wiki', action='index'))
        # Test response...

    def test_view(self):
        response = self.app.get(url(controller='wiki', action='view'))
        # Test response...
        response = self.app.get(url(controller='wiki', action='view'))
