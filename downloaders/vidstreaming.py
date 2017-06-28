import re
import os
import logging

import requests

from furl import furl
from bs4 import BeautifulSoup

from anime_scrapers.downloaders import mp4

site_name = 'vidstream'

BASE_URL = "https://vidstreaming.io"
DOWNLOAD_URL = "https://vidstream.co/download"

qualities = ['1080', '720', '480', '360']


def _try_match_url(link, matchingURL):
    return True if re.match(matchingURL, link) is not None else False


def _try_match_module_section(link, section):
    urls = section['urls']
    matches = [
        section['function'] for x in urls
        if _try_match_url(link, x) is not False
    ]
    return True if len(matches) > 0 else False


def resolve(link):
    for section in internal_matching_urls:
        if _try_match_module_section(link, section):
            logging.info("Found a match for %s" % (link,))
            return section['function'](link)
    return None


def download(link, fname):
    logging.info("Starting download for '%s' under vidstreaming." % (link,))
    sources = resolve(link)['sources']
    if len(sources) > 0:
        source = sources[-1]['link']
    else:
        logging.critical("Can't find sources on vidstreaming!")
        return False
    if source is not None:
        if mp4.download(source, fname):
            return True
    return False


def _parse_quality(title):
    for q in qualities:
        if q in title:
            return q
    return None


def _parse_list_single(data):
    return {
        'link': data['href'],
        'type': 'mp4',
        'quality': _parse_quality(data.text),
    }


def _parse_list_multi(data):
    box = data.find("div", {"class": "mirror_link"})
    sources = box.findAll("a")
    if len(sources) == 0:
        logging.critical("Can't find sources on vidstreaming!")
    return [_parse_list_single(x) for x in sources]


def _scrape_video_sources_id(id):
    params = {
        'id': id,
    }
    request = requests.get(DOWNLOAD_URL, params=params).content
    data = BeautifulSoup(request, 'html.parser')
    return {
        'sources': _parse_list_multi(data),
    }


def _scrape_video_sources(link):
    id = furl(link).args['id']
    logging.info("Found id %s from '%s'" % (id, link,))
    return _scrape_video_sources_id(id)


def _parse_list_embed_single(data):
    return {
        'link': data['src'],
        'type': 'mp4',
        'quality': data['label'],
    }


def _parse_list_embed_multi(data):
    sources = data.findAll("source", {"type": "video/mp4"})
    return [_parse_list_embed_single(x) for x in sources]


def _scrape_video_embed(link):
    data = BeautifulSoup(requests.get(link).content, 'html.parser')
    return {
        'sources': _parse_list_embed_multi(data),
    }

matching_urls = [
    {
        'urls': [
            r'https://vidstream.co/embed.php\?(.*)',
            r'https://vidstreaming.io/embed.php\?id=(.*)',
            ],
        'function': download,
    }
]

internal_matching_urls = [
    {
        'urls': [
            r'https://vidstream.co/download\?id=(.*)',
                ],
        'function': _scrape_video_sources,
    },
    {
        'urls': [
            r'https://vidstream.co/embed.php\?(.*)',
            r'https://vidstreaming.io/embed.php\?id=(.*)',
        ],
        'function': _scrape_video_embed,
    }
]
