import glob
import imp
import logging
import os
import re

import requests

from difflib import SequenceMatcher
from .templates.module_search import ModuleSearch


class ScraperHandler(ModuleSearch):
    # Deals with resolving the scraping of links
    # Automatically resolves with modules in
    # the scrapers folder.
    def __init__(self):
        self._get_modules('scrapers')

    def _search_module(self, query, module):
        return module.search(query)

    # Searches using scraper modules based on query
    def search(self, query, limited_modules=None):
        logging.debug("Starting a search for '%s'." % (query,))
        return [
            self._search_module(query, x)
            for x in self.modules
            if limited_modules is None or x.site_name in limited_modules
        ]

    # Resolves a URL and returns data from
    # proper module and function
    def resolve(self, link, getMethod=requests.get):
        logging.debug(
            "Starting a resolution for '%s'"
            "under scraper_handler." % (link,)
        )
        for module in self.modules:
            functions = self._try_match_module(link, module)
            if len(functions) > 0:
                return functions[0](link, getMethod=getMethod)
        return None


def score_similarity(stringA, stringB):
    return SequenceMatcher(None, stringA, stringB).ratio()

scraper_handler = ScraperHandler()
