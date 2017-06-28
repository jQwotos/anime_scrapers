import re
import logging

import cfscrape as cf

from bs4 import BeautifulSoup

site_name = 'gogoanime'

BASE_URL = "https://gogoanime.io"
SEARCH_URL = "%s/search.html" % (BASE_URL,)
EPISODE_LIST_URL = "%s//load-list-episode" % (BASE_URL,)
SHOW_URL = "%s/category/" % (BASE_URL,)

id_pat = re.compile("var id = (.*?);")
streaming_name_pat = re.compile('"(.*?)"')
epnum_pat = re.compile('episode-(.*?)$')
released_pat = re.compile("Released: ([0-9]+)")

cfscrape = cf.create_scraper()


def _combine_link(url):
    return ("%s%s" % (BASE_URL, url,)).replace(' ', '')


def _parse_released_date(data):
    fullString = str(data.find("p", {"class": "released"}))
    output = re.findall(released_pat, fullString)
    return output[0] if len(output) > 0 else None


def _extract_single_search(data):
    name = data.find('p', {'class': 'name'}).find('a')
    return {
        'link': _combine_link(name['href']),
        'title': name.text,
        'language': 'dub' if 'dub' in name.text.lower() else 'sub',
        'released': _parse_released_date(data),
        'host': site_name,
    }


def _extract_multiple_search(data):
    entries = data.find('ul', {'class': 'items'}).findAll("li")
    return [_extract_single_search(x) for x in entries]


def search(query):
    '''
    Returns all search results based on a query
    [
        {
            'link': 'link to show on gogoanime',
            'title': 'the full title of the show',
            'language': 'either subbed or dubbed',
        }
    ]
    '''
    params = {
        'keyword': query,
        'id': -1,
    }

    data = cfscrape.get(SEARCH_URL, params=params).content
    data = BeautifulSoup(data, 'html.parser')

    return _extract_multiple_search(data)


def _parse_list_single(data):
    return {
        'name': data.find("div", {"class": "name"}).text,
        'link': _combine_link(data['href']),
        'language': data.find("div", {"class": "cate"}).text.lower(),
        'type': 'iframe',
    }


def _parse_list_multi(data):
    episodes = data.findAll("a")
    return [_parse_list_single(x) for x in episodes]


def _load_list_episode(id):
    params = {
        'ep_start': 0,
        'ep_end': 9999999,
        'id': id,
        'default_ep': 0,
    }
    data = cfscrape.get(EPISODE_LIST_URL, params=params).content
    data = BeautifulSoup(data, 'html.parser')
    return _parse_list_multi(data)


def _scrape_show_id(data):
    return re.findall(id_pat, str(data))


def _scrape_title(data):
    return data.find("div", {"class": "anime_info_body_bg"}).find('h1').text


def _scrape_status(data):
    return data.findAll('p', {'class': 'type'})[4].text.replace('Status: ', '')


def _scrape_released(data):
    text = data.findAll('p', {'class': 'type'})[3].text
    return text.replace('Released: ', '')


def _scrape_epNum(url):
    epNum = re.findall(epnum_pat, url)
    return epNum[0] if len(epNum) > 0 else '0'


def _scrape_single_video_source(data):
    return {
        'link': data['data-video'],
        'type': 'iframe'
    }


def _scrape_video_sources(link):
    data = cfscrape.get(link).content
    soupedData = BeautifulSoup(data, 'html.parser')
    sources = soupedData.find("div", {"class", "anime_muti_link"})
    sources = sources.findAll("a")

    return {
        'epNum': _scrape_epNum(link),
        'sources': list(map(
            lambda x: _scrape_single_video_source(x),
            sources)
        ),
    }


def scrape_all_show_sources(link):
    data = cfscrape.get(link).content
    id = _scrape_show_id(data)
    data = BeautifulSoup(data, 'html.parser')
    episodes = _load_list_episode(id)

    return {
        'episodes': [_scrape_video_sources(x['link']) for x in episodes],
        'title': _scrape_title(data),
        'status': _scrape_status(data),
        'host': 'gogoanime',
        'released': _scrape_released(data),
    }

matching_urls = [
    {
        'urls': [r'https://ww[0-9]+.gogoanime.io/category/(.*)'],
        'function': scrape_all_show_sources,
    },
    {
        'urls': [r'https://ww[0-9]+.gogoanime.io//search.html?keyword=(.*)'],
        'function': search,
    },
    {
        'urls': [r'https://ww1.gogoanime.io/(.*)-episode-([0-9]+)'],
        'function': _scrape_video_sources,
    }
]
