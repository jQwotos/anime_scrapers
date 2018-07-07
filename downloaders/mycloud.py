import os
import logging
import re
import subprocess

import requests

from bs4 import BeautifulSoup

types = ['iframe']

MY_CLOUD_PAT = re.compile('<meta property="og:image" content="(.*?)"')

resolutions = ['1080', '720', '480', '360']


def _pick_highest_res(link, headers=None):
    logging.info(
        "Picking the highest res for '%s' under mycloud downloader."
        % (link,)
    )
    testIncrement = 1
    for res in resolutions:
        trialLink = _increment_link(link, testIncrement).replace(
            "{{RESOLUTION}}", res
        )
        if requests.get(trialLink, stream=True, headers=headers).status_code == 200:
            logging.info("Highest quality possible is %s" % (res))
            return link.replace("{{RESOLUTION}}", res)
    # raise ValueError, "Can't find a proper resolution for %s." % (link,)


def _get_direct_link(link, headers=None):
    logging.info(
        "Getting direct link for '%s' under mycloud downloader."
        % (link,)
    )
    data = requests.get(link).content
    details = re.findall(MY_CLOUD_PAT, str(data))[0]
    logging.info("Details are '%s' from '%s'" % (details, link))
    actualLink = details.replace(
        'preview.jpg',
        'hls/{{RESOLUTION}}/{{RESOLUTION}}-{{INCREMENT}}.ts'
    )
    logging.info(
        "Resolved link '%s' under mycloud downloader to '%s'"
        % (link, actualLink,)
    )
    return _pick_highest_res(actualLink, headers)


def _increment_link(link, increment):
    return link.replace('{{INCREMENT}}', '%04d' % (increment,))


def download(link, fname, getMethod=requests.get, **passedArgs):
    headers = {'Referer': link}
    # Downloads a file from MyCloud based on link and filename
    directLink = _get_direct_link(link, headers)
    logging.info("Recieved link of '%s' from '%s'" % (directLink, link,))
    increment = 0
    finished = False

    tempName = "%s.ts.tmp" % (fname,)
    with open(tempName, 'wb') as f:
        while True:
            increment += 1
            newLink = _increment_link(directLink, increment)
            while True:
                try:
                    download = getMethod(newLink, stream=True, timeout=10, headers=headers)
                    break
                except Exception as e:
                    logging.error(
                        "Connection timed out while downloading block %i. With error %s"
                        % (increment, str(e),)
                    )
            if download.status_code == 200:
                f.write(download.content)
                logging.info("Finished writing increment #%i" % (increment))
                finished = True
            else:
                logging.error("FAILED to download increment #%i" % (increment))
                break

    if finished:
        if 'convert' in passedArgs and passedArgs['convert']:
            try:
                subprocess.run(['ffmpeg', '-i', tempName, '%s' % (fname,)])
            except:
                print("Please install FFMPEG")
                return False
            os.remove(tempName)
        else:
            os.rename(tempName, fname)
            return True

matching_urls = [
    {
        'urls': [
            r'https://mcloud.to/embed/(.*)&autostart=true',
            r'https://mcloud.to/embed/(.*)',
        ],
        'function': download,
    }
]
