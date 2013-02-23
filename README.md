Supybot-Wikipedia
=================

Purpose

    Supybot plugin for Wikipedia to query wiki entires and also search.

Instructions

    Should work fine in python 2.6+. Does not use any non-standard modules.
    There are a few config variables (/msg <bot> config search wikipedia) but
    should be fine by default. Searches Wikipedia using their API. You can change
    the base URL to get a different language/use a different MediaWiki location if needed.
    Note: some entries might not display properly.

Commands

    - wikipedia <term>
    - wikisearch [--options] <term>

Suggestions

    /msg <bot> Alias add wiki wikipedia

Example

    <me> wikipedia Germany
    <bot> Germany :: Germany, officially the Federal Republic of Germany (German: Bundesrepublik Deutschland, pronounced ˈdɔʏtʃlant ),
    is a federal parliamentary republic in west-central Europe. The country consists of 16 states, and its capital and largest city is
    Berlin. Germany covers an area of 357,021 square kilometres (137,847 sqmi) and has a largely temperate seasonal climate.
    With 81.8 million (7 more messages)

Notes

    Some source and examples that helped me in designing the plugin (not limited to):
    - https://raw.github.com/samliu/WikipediaSummaryRetriever/master/wikipedia.py
    - http://en.wikipedia.org/w/api.php
    - http://medialab.di.unipi.it/wiki/Wikipedia_Extractor
    - https://github.com/theY4Kman/Yakbot-plugins/blob/faac0bd4fb2599c8adf5aab583ce986aafa037c7/Wikipedia/plugin.py
