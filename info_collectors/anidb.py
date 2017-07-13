import requests
import os
from bs4 import BeautifulSoup
from difflib import SequenceMatcher
import sys

# Constants
BASE_URL = "http://api.anidb.net:9001/httpapi?request=anime"
BASE_PATH = os.path.dirname(os.path.realpath(__file__))
SEARCH_FILE = os.path.join(BASE_PATH, "anime-titles.xml")
IMAGE_URL = "http://img7.anidb.net/pics/anime/"
CLIENT = "fadedanimefinder"
CLIENT_VERSION = 1
MIN_SIMILARITY_RATIO = 0.8

sys.path.append(BASE_PATH)
from _init_anidb import download_list


def _similar(original_txt, matched_txt):
    return SequenceMatcher(None, original_txt, matched_txt).ratio()


def search(query, strict=False):
    '''
    Search for a particular anime among the DB.
    In this module, `strict` is a dummy parameter, and does not do anything.
    Returns a list which contains a dict, containing the show ID and different
    names. Use that ID to get detailed info via getDetailedInfo(ID).
    '''
    download_list.get_file()

    with open(SEARCH_FILE, "rb") as f:
        search_contents = f.read()
    result_page = BeautifulSoup(search_contents, "xml").animetitles

    results = list()
    ratio_list = list()
    for anime in result_page.findAll("anime"):
        highest_ratio = 0
        for title in anime.findAll("title"):
            ratio = _similar(query, title.string)
            if ratio > MIN_SIMILARITY_RATIO:
                if ratio > highest_ratio:
                    highest_ratio = ratio
        if not highest_ratio:
            continue
        ratio_list.append(highest_ratio)
        id = int(anime['aid'])
        titles = [title.string for title in
                  anime.findAll("title", attrs={"type": ["main", "official"]})]
        results.append({"id": id, "titles": titles})
    return [x for y, x in sorted(list(zip(ratio_list, results)), reverse=True)]


def getDetailedInfo(id):
    '''
    Gets a detailed info from the ID provided. A dict is returned with
    the following keys. The type of the value is also mentioned.

    id: int, type: str, start_date: str, end_date: str, other_names: str,
    creators: [{str: str}], permanent_rating: float, image_url: str,
    description: str, recommendations: [{str: str}]
    '''
    request = requests.get(BASE_URL, params={
        "request": "anime",
        "aid": str(id),
        "protover": "1",
        "client": CLIENT,
        "clientver": str(CLIENT_VERSION)
    })
    request.raise_for_status()
    result_page = BeautifulSoup(request.text, "xml")

    results = {
        "id": id,
        "type": result_page.find("type").string,
        "episode_count": result_page.find("episodecount").string,
        "start_date": result_page.find("startdate").string,
        "end_date": result_page.find("enddate").string,
        "other_names": [title.string for title in
                        result_page.find("titles").findAll("title")],
        "creators": [{name['type']: name.string}
                     for name in result_page.find("creators").findAll("name")],
        "permanent_rating": float(result_page.find("ratings")
                                  .find("permanent").string),
        "image_url": IMAGE_URL + result_page.find("picture").string,
        "description": result_page.find("description").string,
        "recommendations": [{rcd['type']: rcd.string} for rcd in
                            result_page.find("recommendations")
                            .findAll("recommendation")]
    }
    return results


matching_urls = [
    {
        'urls': [],
        'function': search,
    },
    {
        'urls': [],
        'function': getDetailedInfo,
    },
]
