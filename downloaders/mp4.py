import os
import sys
import time
import logging

import requests


class Timer:
    def restart(self, request):
        self.length = int(request.headers.get('content-length'))
        self.start = time.clock()

        self.current = 0

    def __init__(self, request):
        self.restart(request)

    def tick(self, chunk_size):
        self.current += chunk_size
        speed = round(self.current // (time.clock() - self.start) / 1000000, 2)
        percentComplete = round((self.current / self.length) * 100, 1)
        sys.stdout.write(
            "\r %s Mbps | %r Percent Complete"
            % (speed, percentComplete)
        )


def download(link, filename):
    logging.info("Starting download for %s." % (link,))
    tempName = "%s.tmp" % (filename,)

    with open(tempName, 'wb') as f:
        request = requests.get(link, stream=True)

        # timer = Timer(request)

        for chunk in request.iter_content(chunk_size=1024):
            # timer.tick(len(chunk))

            if chunk:
                f.write(chunk)
            else:
                logging.error("Failed to a chunk for '%s'." % (link,))
    logging.info("Finished downloading '%s'." % (link,))
    os.rename(tempName, filename)
    return True

matching_urls = [
    {
        'urls': [
            r'http://(.*).animeheaven.eu/video/(.*).mp4(.*)',
            r'https://[0-9]+.bp.blogspot.com(.*)',
        ],
        'function': download,
    },
]
