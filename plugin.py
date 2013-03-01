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
try:
    import xml.etree.cElementTree as ElementTree
except ImportError:
    import xml.etree.ElementTree as ElementTree
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
        wiki = wiki.replace(u'–','-')
        #Remove trailing white spaces
        wiki = ' '.join(wiki.split())
        return wiki

    def _wikiquery(self, opttopic):
        """Perform Wikipedia Query."""

        # prep url.
        url = self.registryValue('wikiUrl')
        urlArgs = {'action': 'query', 'prop': 'extracts',
                   'titles': opttopic, 'format': 'xml',
                   'redirects': '1', 'indexpageids': '1',
                   'exintro': '1', 'explaintext': '1',
                   'meta': 'siteinfo'}
        request_url = url + '?' + self._unicodeurlencode(urlArgs)
        headers={'User-agent': 'Mozilla/5.0 (Windows NT 6.1; rv:15.0) Gecko/20120716 Firefox/15.0a2'}

        # try and fetch url.
        try:
            result = utils.web.getUrl(request_url, headers=headers)
        except utils.web.Error as error:
            self.log.info("I could not open {0} error: {1}".format(request_url, error))
            return ('error', error)

        # parse XML.
        try:
            root = ElementTree.fromstring(result)
        except ElementTree.ParseError as error:
            return ('error', "Error parsing {0}: {1}".format(request_url, error))

        # first parse XML for errors.
        if root.find('query/error'):
            self.log.info("ERROR on wikiquery for {0}: {1}".format(opttopic, root.find('query/error/info')))
            return ('error', "{0} :: {1}".format(root.find('query/error/code'), root.find('query/error/info')))

        # grab XML content from MediaWiki API.
        html = root.find('query/pages/page/extract').text
        title = root.find('query/pages/page').attrib['title']
        articleserver = root.find('query/general').attrib['server']
        articlepath = root.find('query/general').attrib['articlepath']
        wikilink = "http:{0}{1}".format(articleserver, articlepath.replace('$1', title.replace(' ', '_')))  # concat wikilink.
        html = self._removeWikiNoise(html)  # clean html.
        outputcontent = {'text': unicode(title).encode('utf-8'), 'description': unicode(html).encode('utf-8'), 'link': wikilink}
        return ('0', outputcontent)

    def _opensearch(self, opttopic, optnum):
        """Query Mediawiki OpenSearch for topics."""

        # prep url.
        url = self.registryValue('wikiUrl')
        urlArgs = {'action': 'opensearch', 'limit': optnum,
                  'format': 'xml', 'namespace': '0',
                  'search': opttopic}
        request_url = url + '?' + self._unicodeurlencode(urlArgs)
        headers={'User-agent': 'Mozilla/5.0 (Windows NT 6.1; rv:15.0) Gecko/20120716 Firefox/15.0a2'}

        # try and fetch url.
        try:
            result = utils.web.getUrl(request_url, headers=headers)
        except utils.web.Error as error:
            self.log.info("I could not open {0} error: {1}".format(request_url, error))
            return ('error', error)

        # parse XML.
        try:
            root = ElementTree.fromstring(result)
        except ElementTree.ParseError as error:
            return ('error', "Error parsing {0}: {1}".format(request_url, error))

        # find the first item.
        ns = '{http://opensearch.org/searchsuggest2}'
        section = root.find('%sSection' % ns)
        items = section.findall('%sItem' % ns)
        if len(items) < 1:
            return ('error', "No results found for {0}".format(opttopic))
        else:
            items = [{
                'text': unicode(item.find('%sText' % ns).text).encode('utf-8'),
                'description': unicode(item.find('%sDescription' % ns).text).encode('utf-8'),
                'link': unicode(item.find('%sUrl' % ns).text).encode('utf-8')
            } for item in items]

            return ('0', items)

    def wikipedia(self, irc, msg, args, optlist, optinput):
        """[--link] <term>
        Searches Wikipedia for <term>.
        Use --link to display wikipedia link after entry.
        """

        # first, check if we have a url.
        if not self.registryValue('wikiUrl') or self.registryValue('wikiUrl') == "Not set":
            irc.reply("wikipedia URL not set. see 'config help supybot.plugins.Wikipedia.wikiUrl'")
            return

        # handle getopts.
        args = {'link': self.registryValue('showLink')}
        for (key, value) in optlist:
            if key == 'link':
                args['link'] = True

        # do the search.
        results = self._opensearch(optinput, 1)
        if results[0] == 'error':
            irc.reply("ERROR :: {0}".format(results[1]))
            return

        # main logic.
        results = self._wikiquery(results[1][0]['text'])
        if results[0] == 'error':
            irc.reply("ERROR :: {0}".format(results[1]))
            return
        else:
            results = results[1]

        if self.registryValue('disableANSI'):
            irc.reply("{0} :: {1}".format(results['text'], results['description']))
        else:
            irc.reply("{0} :: {1}".format(self._red(results['text']), results['description']))

        if args['link']:
            irc.reply("{0}".format(results['link']))

    wikipedia = wrap(wikipedia, [getopts({'detailed':'', 'link':''}), ('text')])

    def wikisearch(self, irc, msg, args, optlist, optinput):
        """[--num #|--snippets|--link] <term>
        Perform a Wikipedia search for <term>
        Use --num (between 10 and 30) to specify results.
        Use --snippets to display text snippets. (NOTICE: is rather verbose..)
        Use --link to display a link to each article.
        """

        # make sure we have a url.
        url = self.registryValue('wikiUrl')
        if not url or url == "Not set":
            irc.reply("wikipedia URL not set. see 'config help supybot.plugins.Wikipedia.wikiUrl'")
            return

        # arguments for output.
        args = {'num': self.registryValue('numberOfSearchResults'), 'snippets': False, 'link': False}

        # manip args via getopts (optlist)
        if optlist:
            for (key, value) in optlist:
                if key == "num":
                    if 10 <= value <= 30:
                        args['num'] = value
                    else:
                        irc.reply("ERROR: wikisearch --num must be between 10 and 30.")
                        return
                if key == "snippets":
                    args['snippets'] = True
                if key == "link":
                    args['link'] = True

        # do the search.
        results = self._opensearch(optinput, args['num'])
        if results[0] == 'error':
           irc.reply("ERROR :: {0}".format(results[1]))
           return

        # now format the results into a list for output.
        wikiresults = results[1]
        output = []
        for wikiresult in wikiresults:
            tmpstring = wikiresult['text'].encode('utf-8')
            if args['snippets']:
                tmpstring += " - {0}".format(utils.str.normalizeWhitespace(wikiresult['description'].strip()))
            if args['link']:
                tmpstring += " < {0} >".format(wikiresult['link'])
            output.append(tmpstring)

        irc.reply("Search results for {0} :: {1}".format(optinput, " | ".join(output)))

    wikisearch = wrap(wikisearch, [getopts({'num': ('int'), 'link': '', 'snippets': ''}), ('text')])

Class = Wikipedia


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=250:
