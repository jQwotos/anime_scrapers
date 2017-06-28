import requests
from bs4 import BeautifulSoup

# Constants
BASE_URL = "http://api.anidb.net:9001/httpapi?request=anime"
SEARCH_URL = "http://anisearch.outrance.pl/"  # Thank you, whoever created this
IMAGE_URL = "http://img7.anidb.net/pics/anime/"
CLIENT = "fadedanimefinder"
CLIENT_VERSION = 1


def search(query, strict=False):
    '''
    Search for a particular anime among the DB. Enabling strict will display
    only animes containing the exact query.
    Returns a list which contains a dict, containing the show ID and different
    names. Use that ID to get detailed info via getDetailedInfo(ID).
    '''
    request = requests.get(SEARCH_URL, params={
        "task": "search",
        "query": query if not strict else str("\\"+query),
        "langs": "x-jat,en,ja"
    })
    request.raise_for_status()
    result_page = BeautifulSoup(request.text, "xml").animetitles

    results = list()
    for anime in result_page.findAll("anime"):
        id = int(anime['aid'])
        titles = [title.string for title in
                  anime.findAll("title", attrs={"type": ["main", "official"]})]
        results.append({"id": id, "titles": titles})
    return results


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
