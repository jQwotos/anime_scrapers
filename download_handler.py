import logging
import requests

from .templates.module_search import ModuleSearch


class DownloadHandler(ModuleSearch):
    # Deals with resolving downloading of files
    def __init__(self):
        self._get_modules('downloaders')

    def single_download(self, link, abs_path):
        """
        Download a single episode.
        'link' is the full link of it (get it with scraper_handler).
        'abs_path' is full path + filename of downloaded file, example -
        "/home/User/MyDownloadedEpisode.mp4"
        """
        for module in self.modules:
            if self._try_match_module(link, module):
                if module.download(link, abs_path):
                    return True
                return False
        return False

    def resolve(self, data, getMethod=requests.get):
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
                    if module.download(source['link'], fileName, getMethod=getMethod):
                        break

download_handler = DownloadHandler()
