# -*- coding: utf-8 -*-
###
# Copyright (c) 2012, spline
# All rights reserved.
#
#
###

# my libs
import unicodedata
import json
import urllib2
import urllib
import re

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

    def _remove_accents(self, data):
        nkfd_form = unicodedata.normalize('NFKD', unicode(data))
        return u"".join([c for c in nkfd_form if not unicodedata.combining(c)])

    def _red(self, string):
        """return a red string."""
        return ircutils.mircColor(string, 'red')

    def _bu(self, string):
        """bold and underline string."""
        return ircutils.bold(ircutils.underline(string))
    
    def _unicode_urlencode(self, params):
        """
        A unicode aware version of urllib.urlencode.
        Borrowed from pyfacebook :: http://github.com/sciyoshi/pyfacebook/
        """
        if isinstance(params, dict):
            params = params.items()
        return urllib.urlencode([(k, isinstance(v, unicode) and v.encode('utf-8') or v) for k, v in params])

    def unwiki(self, wiki):
        """
       Remove wiki markup from the text.
       """
        wiki = re.sub(r'(?i)\{\{IPA(\-[^\|\{\}]+)*?\|([^\|\{\}]+)(\|[^\{\}]+)*?\}\}', lambda m: m.group(2), wiki)
        wiki = re.sub(r'(?i)\{\{Lang(\-[^\|\{\}]+)*?\|([^\|\{\}]+)(\|[^\{\}]+)*?\}\}', lambda m: m.group(2), wiki)
        wiki = re.sub(r'\{\{[^\{\}]+\}\}', '', wiki)
        wiki = re.sub(r'(?m)\{\{[^\{\}]+\}\}', '', wiki)
        wiki = re.sub(r'(?m)\{\|[^\{\}]*?\|\}', '', wiki)
        wiki = re.sub(r'(?i)\[\[Category:[^\[\]]*?\]\]', '', wiki)
        wiki = re.sub(r'(?i)\[\[Image:[^\[\]]*?\]\]', '', wiki)
        wiki = re.sub(r'(?i)\[\[File:[^\[\]]*?\]\]', '', wiki)
        wiki = re.sub(r'\[\[[^\[\]]*?\|([^\[\]]*?)\]\]', lambda m: m.group(1), wiki)
        wiki = re.sub(r'\[\[([^\[\]]+?)\]\]', lambda m: m.group(1), wiki)
        wiki = re.sub(r'\[\[([^\[\]]+?)\]\]', '', wiki)
        wiki = re.sub(r'(?i)File:[^\[\]]*?', '', wiki)
        wiki = re.sub(r'\[[^\[\]]*? ([^\[\]]*?)\]', lambda m: m.group(1), wiki)
        wiki = re.sub(r"''+", '', wiki)
        wiki = re.sub(r'(?m)^\*$', '', wiki)
       
        return wiki
   
    def unhtml(self, html):
        """
       Remove HTML from the text.
       """
        html = re.sub(r'(?i)&nbsp;', ' ', html)
        html = re.sub(r'(?i)<br[ \\]*?>', '\n', html)
        html = re.sub(r'(?m)<!--.*?--\s*>', '', html)
        html = re.sub(r'(?i)<ref[^>]*>[^>]*<\/ ?ref>', '', html)
        html = re.sub(r'(?m)<.*?>', '', html)
        html = re.sub(r'(?i)&amp;', '&', html)
       
        return html
   
    def punctuate(self, text):
        """
       Convert every text part into well-formed one-space
       separate paragraph.
       """
        text = re.sub(r'\r\n|\n|\r', '\n', text)
        text = re.sub(r'\n\n+', '\n\n', text)
       
        parts = text.split('\n\n')
        partsParsed = []
       
        for part in parts:
            part = part.strip()
           
            if len(part) == 0:
                continue
           
            partsParsed.append(part)
       
        return '\n\n'.join(partsParsed)

    def _parse(self, text):
        '''Formats wikipedia text by removing links and styling'''
        text = re.sub(r'\<ref.*?\</ref\>', '', text) #removes spanning ref tags
        text = re.sub(r'\<.*?\>', '', text) #removes individual tags ex <ref />
        text = re.sub(r'\{\{[^{{]*?\}\}', '', text) #removes {{qwerty}}
        text = re.sub(r'\{\{[^{{]*?\}\}', '', text) #repeated to removed embedded {{}}
        text = re.sub(r'\{\{[^{{]*?\}\}', '', text)
        text = re.sub(r'\[\[(?P<tag>[^|]*?)\]\]', '\g<tag>', text) #replaces [[tag]] with tag if | not in tag
        text = re.sub(r'\[\[(File|Image).*?\[\[.*?\]\].*?\]\]', '', text) #removes [[File/Image...[[...]]...]]
        text = re.sub(r'\[\[(File|Image).*?\]\]', '', text) #removes [[Files/Image...]]
        text = re.sub(r'\[\[.*?\|(?P<tag2>.*?)\]\]', '\g<tag2>', text) #replaces [[link|text]] with text
        text = text.replace('\'\'\'', '') #removes '''
        text = text.replace('&nbsp;', ' ') #removes no break spaces
        text = text.replace(u'–','-')
        return text.strip()
    
    def wikipedia(self, irc, msg, args, optlist, optinput):
        """<term>
        Searches Wikipedia for <term>. 
        """
        
        url = self.registryValue('wikiUrl')
        if not url or url == "Not set":
            irc.reply("Wolfram Alpha API key not set. see 'config help supybot.plugins.Wikipedia.wikiUrl'")
            return
             
        urlArgs = {'action':'query','prop':'revisions','rvsection':'0','titles':optinput,'rvprop':'content','format':'json','redirects':'1'}
                    
        request = urllib2.Request(url, data=self._unicode_urlencode(urlArgs), headers={'User-Agent':'Mozilla/5.0'})
        result = urllib2.urlopen(request)
        jsondata = json.loads(result.read().decode('utf-8'))

        if 'redirects' in jsondata['query'].keys():
            redirectsto = jsondata['query']['redirects'][0]['to']
            redirectsfrom = jsondata['query']['redirects'][0]['from']
            irc.reply("Redirects: {0} from {1}".format(redirectsto, redirectsfrom))

        resultkeys = []
        for page in jsondata['query']['pages']:
            resultkeys.append(page)

        if len(resultkeys) < 1:
            irc.reply("Something broke getting results looking up: {0}".format(optinput))
            return
        
        output = jsondata['query']['pages'][resultkeys[0]]
        outputtitle = str(output['title'])
        
        outputcontent = output['revisions'][0]['*']
        outputcontent = self._remove_accents(self._parse(outputcontent))
        
        irc.reply("{0}".format(outputtitle))
        irc.reply("{0}".format(outputcontent))
        
    wikipedia = wrap(wikipedia, [getopts({}), ('text')])
    
    def wikisearch(self, irc, msg, args, optlist, optinput):
        pass
    wikisearch = wrap(wikisearch, [getopts({}), ('text')])

Class = Wikipedia


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=250:
