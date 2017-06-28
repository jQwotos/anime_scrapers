import re
import logging

import requests

from bs4 import BeautifulSoup as bs

site_name = "9anime.to"

BASE_URL = 'https://9anime.to'
SEARCH_URL = '%s/search' % (BASE_URL,)
INFO_API_URL = "%s/ajax/episode/info" % (BASE_URL,)


class NineAnimeUrlExtender:
    '''

    NineAnimeUrlExtender was written by
    DxCx (https://github.com/DxCx)
    for https://github.com/DxCx/plugin.video.9anime
    permission was granted for usage. Please
    support the original creator

    '''
    @classmethod
    def get_extra_url_parameter(cls, id, update, ts):
        DD = 'gIXCaNh'
        params = [('id', str(id)), ('update', str(update)), ('ts', str(ts))]

        o = cls._s(DD)
        for i in params:
            o += cls._s(cls._a(DD + i[0], i[1]))

        return o

    @classmethod
    def _s(cls, t):
        i = 0
        for (e, c) in enumerate(t):
            i += ord(c) * e + e
        return i

    @classmethod
    def _a(cls, t, e):
        n = 0
        for i in range(max(len(t), len(e))):
            n += ord(e[i]) if i < len(e) else 0
            n += ord(t[i]) if i < len(t) else 0
        return format(n, 'x')  # convert n to hex string


def _parse_search_single(data):
    img = data.find("img")
    nameAnchor = data.find("a", {"class": "name"})
    lang = data.find('div', {'class': 'lang'})
    lang = lang.text if lang is not None else 'sub'

    return {
        'title': nameAnchor.text,
        'link': nameAnchor['href'],
        'language': lang.lower(),
        'host': site_name,
        'poster': img['src']
    }


def _parse_search_multi(data):
    return [
        _parse_search_single(x)
        for x in data.findAll("div", {"class": "item"})
    ]


def search(query):
    params = {
        'keyword': query,
    }
    data = bs(requests.get(SEARCH_URL, params=params).content)

    return _parse_search_multi(data)


def _scrape_episode_source(data):
    return {
        'link': data['file'],
        'type': data['type'],
        'quality': data['label'],
    }


def _scrape_episode_sources(data):
    request = requests.get(data['grabber'], params=data['params']).json()
    return [_scrape_episode_source(x) for x in request['data']]


def _scrape_episode_info(id, ts, update):
    logging.debug("'%s' is performing a info grab for '%s'" % (site_name, id,))
    params = {
        'id': id,
        'ts': ts,
        'update': update,
        '_': NineAnimeUrlExtender.get_extra_url_parameter(id, update, ts),
    }
    data = requests.get(INFO_API_URL, params=params)

    if data.status_code == 200:
        data = data.json()
        if data['target'] == '' or data['type'] == 'direct':
            return _scrape_episode_sources(data)
        else:
            return {
                'link': data['target'],
                'type': data['type'],
            }


def _parse_server_single_episode(data, ts, update):
    anchor = data.find("a")
    id = anchor['data-id']
    output = {
        'data-id': id,
        'epNum': anchor.text,
        'sources': _scrape_episode_info(id, ts, update),
    }
    return output if output['sources'] is not None else None


def _parse_server_episodes(data, ts, update):
    episodes = data.findAll("li")
    sources = [_parse_server_single_episode(x, ts, update) for x in episodes]
    if len(sources) > 0:
        return list(filter(None, sources))


def _scrape_all_servers(data, ts, update):
    servers = data.findAll("div", {"class": "server row"})
    sourcedServers = [_parse_server_episodes(x, ts, update) for x in servers]
    return list(filter(None, sourcedServers))


def format_combine_multi(unformatedOutput):
    output = []
    for ep in unformatedOutput:
        output.append({
            'epNum': str(int(ep)),  # remove leading 0s
            'sources': unformatedOutput[ep]
        })
    return output


def combine_multi(servers):
    unformatedOutput = {}
    for server in servers:
        for ep in server:
            if ep['epNum'] not in unformatedOutput:
                unformatedOutput[ep['epNum']] = ep['sources']
            else:
                unformatedOutput[ep['epNum']] += ep['sources']

    return format_combine_multi(unformatedOutput)


def _scrape_title(data):
    return data.find('h1', {'class': 'title'}).text


def scrape_all_show_sources(link):
    logging.info(
        "A request for '%s' was made under %s scraper." %
        (link, site_name)
    )
    data = bs(requests.get(link).content, 'html.parser')
    body = data.find('body')
    ts = body['data-ts']
    update = '0'
    servers = _scrape_all_servers(data, ts, update)
    return {
        'episodes': combine_multi(servers),
        'title': _scrape_title(data),
        'host': site_name,
    }

matching_urls = [
    {
        'urls': [
            r'https://9anime.to/watch/(.*).(.*)',
            r'https://9anime.is/watch/(.*).(.*)'
        ],
        'function': scrape_all_show_sources,
    },
]
