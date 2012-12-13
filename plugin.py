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

    def _removeaccents(self, string):
        nkfd_form = unicodedata.normalize('NFKD', unicode(string))
        return u"".join([c for c in nkfd_form if not unicodedata.combining(c)])

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
        return urllib.urlencode([(k, isinstance(v, unicode) and v.encode('utf-8') or v) for k, v in params])

    def _unwiki(self, wiki):
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
        wiki = re.sub(r'\<ref.*?\</ref\>', '', wiki) #removes spanning ref tags
        wiki = re.sub(r'\<.*?\>', '', wiki) #removes individual tags ex <ref />
        wiki = re.sub(r'\{\{[^{{]*?\}\}', '', wiki) #removes {{qwerty}}
        wiki = re.sub(r'\{\{[^{{]*?\}\}', '', wiki) #repeated to removed embedded {{}}
        wiki = re.sub(r'\{\{[^{{]*?\}\}', '', wiki)
        wiki = re.sub(r'\[\[(?P<tag>[^|]*?)\]\]', '\g<tag>', wiki) #replaces [[tag]] with tag if | not in tag
        wiki = re.sub(r'\[\[(File|Image).*?\[\[.*?\]\].*?\]\]', '', wiki) #removes [[File/Image...[[...]]...]]
        wiki = re.sub(r'\[\[(File|Image).*?\]\]', '', wiki) #removes [[Files/Image...]]
        wiki = re.sub(r'\[\[.*?\|(?P<tag2>.*?)\]\]', '\g<tag2>', wiki) #replaces [[link|text]] with text
        wiki = wiki.replace('\'\'\'', '') #removes '''
        wiki = wiki.replace('&nbsp;', ' ') #removes no break spaces
        wiki = wiki.replace(u'–','-')
        return wiki
   
    def _unhtml(self, html):
        """
        Remove HTML from the text.
        """
        html = re.sub(r'(?i)&nbsp;', ' ', html)
        html = re.sub(r'(?i)<br[ \\]*?>', '\n', html)
        html = re.sub(r'(?m)<!--.*?--\s*>', '', html)
        html = re.sub(r'(?i)<ref[^>]*>[^>]*<\/ ?ref>', '', html)
        html = re.sub(r'(?m)<.*?>', '', html)
        html = re.sub(r'(?i)&amp;', '&', html)
        #html = re.sub(r'[ ]+', ' ', html) # multiplespaces
        html = html.replace(u'–','-') # unicode - 
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
        text = text.replace("\'","'")
        text = re.sub('<[^>]+>', '', text)
        text = re.sub(' ([.,!?\'])', '\\1', text)
        return text.strip()
    
    # https://en.wikipedia.org/w/api.php?action=query&prop=extracts&titles=Albert%20Einstein&explaintext&format=json
    # http://en.wikipedia.org/w/api.php?format=json&action=query&prop=revisions&titles=Stack%20Overflow&rvprop=content&rvsection=0&rvparse
    # https://github.com/j2labs/wikipydia/blob/master/wikipydia/__init__.py
    # http://en.wikipedia.org/w/api.php?action=parse&page=Germanist&format=json&redirects=1&disablepp=1&section=0
    def wikipedia(self, irc, msg, args, optlist, optinput):
        """<term>
        Searches Wikipedia for <term>. 
        """
        
        # works by default but make sure we have a wikiUrl.
        url = self.registryValue('wikiUrl')
        if not url or url == "Not set":
            irc.reply("Wolfram Alpha URL not set. see 'config help supybot.plugins.Wikipedia.wikiUrl'")
            return
             
        urlArgs = {'action':'parse','page':optinput,'format':'json','redirects':'1','disablepp':'1'} #,'section':'0'}
                    
        request = urllib2.Request(url, data=self._unicodeurlencode(urlArgs), headers={'User-Agent':'Mozilla/5.0'})
        self.log.info(url)
        self.log.info(str(urlArgs))
        result = urllib2.urlopen(request)
        jsondata = json.loads(result.read())
        
        # look to see if there is an error and handle it.
        jsonerror = jsondata.get('error', None)
        if jsonerror:
            errorcode = jsonerror['code']
            errorinfo = jsonerror['info']
            irc.reply("ERROR looking up {0} :: {1} looking up: {2}".format(optinput, errorcode, errorinfo))
            return
            
        # if no errors, move into parse with one last error check.
        jsondata = jsondata.get('parse', None)
        if not jsondata:
            irc.reply("Big error. Check logs/code.")
            return
      
        # handle redirects
        redirects = jsondata.get('redirects', None)
        if redirects:
            # redirectsto = redirects.get('to', None)
            # redirectsfrom = redirects.get('from', None)
            irc.reply(redirects)
            
        outputcontent = jsondata['text']['*']
        outputtitle = jsondata['displaytitle']
        outputcontent = self._unhtml(outputcontent)
        outputcontent = outputcontent.replace('\n','').replace('\r','')
        outputcontent = self._unwiki(outputcontent)
        outputcontent = self._removeaccents(outputcontent.encode('ascii', 'ignore'))
        
        irc.reply("{0}".format(outputtitle))
        irc.reply("{0}".format(outputcontent))
        
    wikipedia = wrap(wikipedia, [getopts({}), ('text')])
    
    def wikisearch(self, irc, msg, args, optlist, optinput):
        # http://codereview.stackexchange.com/questions/17861/python-class-review-wiki-api-getter
        # http://en.wikipedia.org/w/api.php?action=opensearch&search=Germany&format=xml
        # http://en.wikipedia.org/w/api.php?action=query&list=search&srsearch=Germany&srwhat=text&srlimit=10&format=json
        #from SPARQLWrapper import SPARQLWrapper, JSON

        #sparql = SPARQLWrapper("http://dbpedia.org/sparql")
        #sparql.setQuery("""
        #    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        #    SELECT ?label
        #    WHERE { <http://dbpedia.org/resource/Asturias> rdfs:label ?label }
        #    """)
        #sparql.setReturnFormat(JSON)
        #results = sparql.query().convert()

        #for result in results["results"]["bindings"]:
        #    print(result["label"]["value"])
        pass
    wikisearch = wrap(wikisearch, [getopts({}), ('text')])

Class = Wikipedia


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=250:
