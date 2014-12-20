###
# see LICENSE.txt file for details.
###

from supybot.test import *

class WikipediaTestCase(PluginTestCase):
    plugins = ('Wikipedia',)

    def testWikipedia(self):
        conf.supybot.plugins.Wikipedia.disableANSI.setValue('True')
        self.assertRegexp('wikipedia IRC', 'Internet Relay Chat :: Internet Relay Chat')
