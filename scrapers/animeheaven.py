import re
import logging

import requests

from bs4 import BeautifulSoup

site_name = 'animeheaven'

BASE_URL = "http://animeheaven.eu"
SEARCH_URL = "%s/search.php" % (BASE_URL,)

# source_pat = re.compile("<source src='(.*?)'")
source_pat = re.compile("document.write\(\"<a  class='an' href='(.*?)'")
epnum_pat = re.compile('e=(.*?)$')
status_pat = re.compile('<div class="textd">Status:</div><div class="textc">(.*?)</div>')
released_pat = re.compile('<div class="textd">Year:</div><div class="textc">(.*)</div>')


def _combine_link(url):
    # Combines the relative url with the base url
    return ("%s/%s" % (BASE_URL, url,)).replace(' ', '%20')


def _extract_single_search(data):
    # Takes in bs4 data of a single search result
    # and returns a formated dict
    anchor = data.find("a")
    img = anchor.find("img")
    name = img['alt']
    return {
        'link': _combine_link(anchor['href']),
        'title': name,
        'language': 'dub' if 'dub' in name.lower() else 'sub',
        'host': site_name,
        'poster': _combine_link(img['src']),
    }


def _extract_multiple_search(data):
    # Takes in search result page
    # and returns list of formated results
    entries = data.findAll('div', {'class': 'iep'})
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
    logging.info("A query for %s was made under animeheaven" % (query,))
    params = {'q': query}
    data = requests.get(SEARCH_URL, params=params).content
    data = BeautifulSoup(data, 'html.parser')

    return _extract_multiple_search(data)


def _parse_list_single(data):
    return {
        'name': data.find("div", {"class": "infoept2"}),
        'link': _combine_link(data['href']),
    }


def _parse_list_multi(data):
    box = data.find("div", {"class": "infoepbox"})
    episodes = box.findAll("a")
    return [_parse_list_single(x) for x in episodes]


def _hex_source_to_str(source_url):
    return bytes(source_url, 'utf-8').decode('unicode_escape')


def _scrape_single_video_source(data):
    source_url = re.findall(source_pat, str(data))
    return {
        'link': _hex_source_to_str(source_url[0]) if len(source_url) > 0 else None,
        'type': 'mp4',
    }


def _scrape_epNum(url):
    epNum = re.search(epnum_pat, url)
    return epNum.group().replace('e=', '') if epNum is not None else None

def _parse_multi_video_sources(data):
    return [_scrape_video_sources(x) for x in data]


def _scrape_video_sources(link):
    # Scrapes details on a specific
    # episode of a show based on link
    data = BeautifulSoup(requests.get(link).content)
    logging.info("Scraping video sources for %s under animeheaven" % (link,))    # test = data.findall("div", {'class': 'centerf2'})
    sources = data.find("div", {'class': 'centerf2'}).findAll('script')

    return {
        'epNum': _scrape_epNum(link),
        'sources': [_scrape_single_video_source(x) for x in sources],
    }

def _scrape_title(data):
    # Takes in bs4 show page
    # and returns the title of
    # the show
    return data.find("div", {"class": "infodes"}).text


def _scrape_released(data):
    # Takes in bs4 show page and
    # returns released year as string
    box = data.findAll("div", {"class": 'infodes2'})
    if len(box) < 1: return None
    box = box[1]
    released_date = re.search(released_pat, str(box))
    return released_date.group() if released_date is not None else Noneß


def _scrape_status(data):
    # Takes in bs4 show page and
    # return status of the show
    box = data.findAll("div", {"class": "infodes2"})
    if len(box) < 1: return Noneß
    box = box[1]
    status = re.search(status_pat, str(box))
    return status.group() if status is not None else None


def scrape_all_show_sources(link):
    # Returns all show's sources and details
    # based on the link of the show.
    logging.info(
        "A request for '%s' was made to animeheaven scraper."
        % (link,)
    )
    data = BeautifulSoup(requests.get(link).content, 'html.parser')
    episodes = _parse_list_multi(data)
    logging.debug("Got %i links for %s" % (len(episodes), link,))

    return {
        'episodes': [_scrape_video_sources(x['link']) for x in episodes],
        'title': _scrape_title(data),
        'status': _scrape_status(data),
        'host': 'animeheaven',
        'released': _scrape_released(data),
    }

matching_urls = [
    {
        'urls': [r'http://animeheaven.eu/i.php\?a=(.*)'],
        'function': scrape_all_show_sources,
    },
    {
        'urls': [r'http://animeheaven.eu/search.php\?q=(.*)'],
        'function': search,
    },
    {
        'urls': [r'http://animeheaven.eu/watch.php\?a=(.*)&e=([0-9]+)'],
        'function': _scrape_video_sources,
    }
]
