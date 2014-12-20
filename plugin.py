# -*- coding: utf-8 -*-
###
# Copyright (c) 2013, spline
# All rights reserved.
#
#
###

# my libs
import re
from collections import defaultdict
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

    def _unicodeurlencode(self, params):
        """
        A unicode aware version of urllib.urlencode.
        Borrowed from pyfacebook :: http://github.com/sciyoshi/pyfacebook/
        """
        if isinstance(params, dict):
            params = params.items()
        return utils.web.urlencode([(k, isinstance(v, unicode) and v.encode('utf-8') or v) for k, v in params])

    def _removeWikiNoise(self, wiki):
        """Remove wikipedia cruft in output to display better."""
        wiki = re.sub(r'(?i)\{\{IPA(\-[^\|\{\}]+)*?\|([^\|\{\}]+)(\|[^\{\}]+)*?\}\}', lambda m: m.group(2), wiki)
        wiki = re.sub(r'(?i)\{\{Lang(\-[^\|\{\}]+)*?\|([^\|\{\}]+)(\|[^\{\}]+)*?\}\}', lambda m: m.group(2), wiki)
        wiki = re.sub(r'Coordinates:.*?\n\n', '',wiki)
        wiki = re.sub(r'\{\{[^\{\}]+\}\}', '', wiki)
        wiki = re.sub(r'(?m)\{\{[^\{\}]+\}\}', '', wiki)
        wiki = re.sub(r'(?m)\{\|[^\{\}]*?\|\}', '', wiki)
        wiki = re.sub(r'\(.?\[Image\].*?\)', '', wiki)
        wiki = re.sub(r'\s\(.*?\[Listen\].*?\)', '', wiki)
        wiki = re.sub(r'(?i)\[\[Image:[^\[\]]*?\]\]', '', wiki)
        wiki = re.sub(r'(?i)\[\[File:[^\[\]]*?\]\]', '', wiki)
        wiki = re.sub(r'\[\[[^\[\]]*?\|([^\[\]]*?)\]\]', lambda m: m.group(1), wiki)
        wiki = re.sub(r'\[\[([^\[\]]+?)\]\]', lambda m: m.group(1), wiki)
        wiki = re.sub(r'\[\[([^\[\]]+?)\]\]', '', wiki)
        wiki = re.sub(r'(?i)File:[^\[\]]*?', '', wiki)
        wiki = re.sub(r'\[[^\[\]]*? ([^\[\]]*?)\]', lambda m: m.group(1), wiki)
        wiki = re.sub(r"''+", '', wiki)
        wiki = re.sub(r'(?m)^\*$', '', wiki)
        #Remove HTML from the text.
        wiki = re.sub(r'(?i)&nbsp;', ' ', wiki)
        wiki = re.sub(r'(?i)<br[ \\]*?>', '\n', wiki)
        wiki = re.sub(r'(?m)<!--.*?--\s*>', '', wiki)
        wiki = re.sub(r'(?i)<ref[^>]*>[^>]*<\/ ?ref>', '', wiki)
        wiki = re.sub(r'(?m)<.*?>', '', wiki)
        wiki = re.sub(r'(?i)&amp;', '&', wiki)
        #Remove -
        wiki = wiki.replace('–', '-')
        #Remove trailing white spaces
        wiki = ' '.join(wiki.split())
        return wiki

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
            irc.reply("ERROR: {0} yielded a disambiguation page. Suggestions: {1}".format(query, e.options))
            return
        except wikipedia.exceptions.PageError as e:
            irc.reply("ERROR: {0} yielded a error. Suggestions: {1}".format(query, e))
            return
        # now if we did get a page, lets print the summary.
        title = wp.title.encode('utf-8')
        content = wp.content.encode('utf-8')
        # output.
        if self.registryValue('disableANSI'):
            irc.reply("{0} :: {1}".format(title, content))
        else:
            irc.reply("{0} :: {1}".format(title, content))

    wikipedia = wrap(wikipedia, [getopts({'lengh': ('int')}), ('text')])


Class = Wikipedia


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=250:
