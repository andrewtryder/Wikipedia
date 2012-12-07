# -*- coding: utf-8 -*-
###
# Copyright (c) 2012, spline
# All rights reserved.
#
#
###

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


Class = Wikipedia


# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:
