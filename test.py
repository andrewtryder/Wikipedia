###
# Copyright (c) 2012-2013, spline
# All rights reserved.
#
#
###

from supybot.test import *

class WikipediaTestCase(PluginTestCase):
    plugins = ('Wikipedia',)

    def testWikipedia(self):
        conf.supybot.plugins.Wikipedia.disableANSI.setValue('True')
        self.assertRegexp('wikipedia IRC', 'Internet Relay Chat :: Internet Relay Chat')
        self.assertRegexp('wikisearch IRC', 'Search results for IRC :: Internet Relay Chat \| IRCAM')


# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
