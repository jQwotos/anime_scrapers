# anime-scrapers

Anime scrapers is a collection of scrapers that have been all unified.

## Table of Contents
- [Index](#Index)
- [Functions](#Functions)
- [Contributing](#Contributing)
    - [URL Handling (matching_urls)](#URLHandling)
- [Credits](#Credits)
## Usage
```
python3 animescraper.py [link]
```

### Functions
There are three primary function calls in the scrapers

```
scrape_all_show_sources(link):
  return {
    'episodes': [
      {
        'epNumber', 'number as a string',
        'sources', sourceType
      }
    ],
    'title': 'title of the show',
    'status': 'status of the show',
    'host': 'host such as gogoanime',
    'released': 'year released as a string',
  }
```

```
search(query):
  return [
    {
      'link': 'link to the show',
      'title': 'title of the show',
      'language': 'sub or dub',
    },
  ]
```

```
_scrape_video_sources(link):
  return {
    'epNum': 'episode number as a string',
    'sources': sourceType
  }
```

SourceTypes are in the following format.
```
[
  {
    'link': 'link to the mp4 or iframe embed',
    'type': 'mp4 or iframe',
  }
]
```

For information gathering, use the `info_handler.py`. The functions are -

```
# strict is a boolean, which if True, searches for exact query only.
search(query, strict):
  return [
    {
      'id': 'id of the show (int)',
      'titles': 'Other names of the show (str)',
    }
  ]
```

```
getDetailedInfo(id):
  return [
    {
      'id': 'return the id from the parameter (int)',
      'other-show-stuff': 'Other info related to show.
      			  See anidb.py in info_collectors for example',
      ...
    }
  ]
```

## Contributing

### URL Handling (matching_urls)
Most functions will go through functions until there is a matching url schema. Each scraper contains the following variable which is used by the handler in order to identify the correct module to use when resolving links.
```
matching_urls = [
  {
    'urls': ['regex match expression'],
    'function': function that should be called,
  },
]
```

### Adding a Scraper
Scrapers handle search queries, scraping episodes from hosts and scraping sources from those episodes.

Scrapers should have the above three different functions
- search
- _scrape_video_sources
- scrape_all_show_sources

Scrapers should also have the following variables
- matching_urls

- Scrapers should be put into the `scrapers` folder

### Adding a downloader
Downloaders are what extract the direct link the the video file or download the file based off a filename.

Downloaders need these functions, they do not return a value.
- download
```
download(link, filename):
```

Downloaders also need the following variables
- matching_urls

- Put them in the `downloaders` folder

### Adding an information collector
Information collectors collect various information about a particular anime series/movie.

They need these functions, which are mentioned in details above.
- search
- getDetailedInfo

Info collectors should also have the following variables
- matching_urls

- Put them in the `info_collectors` folder

## Credits
- jQwotos
- FadedCoder
- DxCx (NineAnimeUrlExtender)
