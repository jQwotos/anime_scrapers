import glob
import imp
import logging
import os
import re

from random import randint

from .templates.module_search import ModuleSearch


class DownloadHandler(ModuleSearch):
    # Deals with resolving downloading of files
    # Automatically creates file names, and
    # resolves with modules in downloaders
    # folder.
    def __init__(self):
        self._get_modules('downloaders')

    def resolve(self, data):
        logging.info(
            "Trying to resolve '%s'"
            % (data['epNum'])
         )
        for module in self.modules:
            for source in data['sources']:
                logging.info(
                    "Trying to resolve '%s' source."
                    % (source['link'])
                )
                if self._try_match_module(source['link'], module):
                    logging.info(
                        "Found a matching module for '%s'."
                        % (source,)
                    )
                    # PEP8 Too long
                    fileName = "%s.mp4" % (data['epNum'],) if 'epNum' in data else source
                    if module.download(source['link'], fileName):
                        break

download_handler = DownloadHandler()
