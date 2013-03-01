###
# Copyright (c) 2012-2013, spline
# All rights reserved.
#
#
###

import supybot.conf as conf
import supybot.registry as registry
from supybot.i18n import PluginInternationalization, internationalizeDocstring

_ = PluginInternationalization('Wikipedia')

def configure(advanced):
    # This will be called by supybot to configure this module.  advanced is
    # a bool that specifies whether the user identified himself as an advanced
    # user or not.  You should effect your configuration by manipulating the
    # registry as appropriate.
    from supybot.questions import expect, anything, something, yn
    conf.registerPlugin('Wikipedia', True)


Wikipedia = conf.registerPlugin('Wikipedia')
conf.registerGlobalValue(Wikipedia,'disableANSI',registry.Boolean(False, """Do not display any ANSI (color/bold) in output."""))
conf.registerGlobalValue(Wikipedia,'numberOfSearchResults',registry.Integer(10, """Max number of search results for Wikipedia. Defaults to 10."""))
conf.registerGlobalValue(Wikipedia,'wikiUrl',registry.String('http://en.wikipedia.org/w/api.php', """URL of the website from where you want to pull pages (usually: your language's wikipedia)"""))
conf.registerGlobalValue(Wikipedia,'showLink',registry.Boolean(False, """Show wikipedia link after displaying entry on query?"""))

# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=250:
