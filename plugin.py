###
# see LICENSE.txt file for details.
###

from __future__ import unicode_literals
# my libs
import re
import wikipedia
# supybot libs
import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks
from supybot.i18n import PluginInternationalization, internationalizeDocstring

_ = PluginInternationalization('Wikipedia')

@internationalizeDocstring
class Wikipedia(callbacks.Plugin):
    """Add the help for "@plugin help Wikipedia" here
    This should describe *how* to use this plugin."""
    threaded = True

    def _red(self, string):
        """return a red string."""
        return ircutils.mircColor(string, 'red')

    def _bu(self, string):
        """bold and underline string."""
        return ircutils.bold(ircutils.underline(string))

    def _wf(self, s):
        """
        Fix up string for output.
        """

        s = s.replace('\n', '')
        return s

    ###################
    # PUBLIC COMMANDS #
    ###################

    def wikipedia(self, irc, msg, args, optlist, query):
        """<query>

        Display Wikipedia entry.
        """

        # handle optlist.
        lang = self.registryValue('lang')
        # handle getopts.
        args = {}
        args['link'] = False
        args['length'] = 400
        # iterate over them.
        for (key, value) in optlist:
            if key == 'link':
                args['link'] = True
            if key == 'length':
                if value > 400:
                    value = 400
                elif value < 1:
                    value = 400
                args['length'] = value

        try:
            # grab default language via config.
            wikipedia.set_lang(lang)
            wp = wikipedia.page(query)
        # check if its a disambig.
        except wikipedia.exceptions.DisambiguationError as e:
            irc.reply("ERROR: {0} yielded a disambiguation page. Suggestions: {1}".format(query, ", ".join([i for i in e.options])))
            return
        except wikipedia.exceptions.PageError as e:
            irc.reply("ERROR: {0} yielded a error. Suggestions: {1}".format(query, e))
            return
        # now if we did get a page, lets print the summary.
        title = wp.title
        content = self._wf(wp.content)
        # output.
        if self.registryValue('disableANSI'):
            irc.reply("{0} :: {1}".format(title, content))
        else:
            irc.reply("{0} :: {1}".format(self._red(title), content))

    wikipedia = wrap(wikipedia, [getopts({'length': ('int')}), ('text')])


Class = Wikipedia


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=250:
