import logging

import requests

from bs4 import BeautifulSoup as bs

site_name = "9anime.is"

BASE_URL = 'https://9anime.is'
SEARCH_URL = '%s/search' % (BASE_URL,)
INFO_API_URL = "%s/ajax/episode/info" % (BASE_URL,)


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


def _scrape_episode_info(id):
    logging.debug("'%s' is performing a info grab for '%s'" % (site_name, id,))
    params = {'id': id}
    data = requests.get(INFO_API_URL, params=params)
    if data.status_code == 200:
        data = data.json()
        if data.get('target') == '' or data.get('type') == 'direct':
            return _scrape_episode_sources(data)
        else:
            return {
                'link': data.get('target'),
                'type': data.get('type'),
            }


def _parse_server_single_episode(data):
    anchor = data.find("a")
    id = anchor['data-id']
    output = {
        'data-id': id,
        'epNum': anchor.text,
        'sources': _scrape_episode_info(id),
    }
    return output if output['sources'] is not None else None


def _parse_server_episodes(data):
    episodes = data.findAll("li")
    sources = [_parse_server_single_episode(x) for x in episodes]
    if len(sources) > 0:
        return list(filter(None, sources))


def _scrape_all_servers(data):
    servers = data.findAll("ul", {"class": "episodes range active"})
    sourcedServers = [_parse_server_episodes(x) for x in servers]
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
    print(servers)
    for server in servers:
        for ep in server:
            if ep['epNum'] not in unformatedOutput:
                unformatedOutput[ep['epNum']] = [ep['sources']]
            else:
                unformatedOutput[ep['epNum']] += [ep['sources']]

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
    servers = _scrape_all_servers(data)
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
