# anime-scrapers

Anime scrapers is a collection of scrapers that have been all unified.

## Table of Contents
- [Index](#Index)
- [Functions](#Functions)
  - [Handlers](#Handlers)
  - [Individual Scraper Functions](#Individual-Scraper-Functions)
- [Contributing](#Contributing)
    - [URL Handling (matching_urls)](#URLHandling)
- [Credits](#Credits)

## Installation

### Mac (OSX)
- Install [Brew](https://brew.sh/)
- Install python3
  - `brew install python3`
- Continue to general installation

### General Installation
- Clone repository
  - `git clone https://github.com/jQwotos/anime_scrapers`
- Nav into repo
  - `cd anime_scrapers`
- Install required python packages
  - `pip install -r requirements.txt`

## Usage

anime_scrapers is the backend that is to be used by other applications. You can however use it directly if you want by using the python shell, but it's better to use an application.

### Functions

#### Handlers

Handlers are all classes, however each of them also have premade variables so you don't need to create a new object each time.

For example `scraper_handler.py` has

`class ScraperHandler():`

and

`var scraper_handler`

##### scraper_handler
- `search(query, limited_modules[])`
  - Searches all scraper modules (or specified ones)
- `resolve(link)`
  - Finds matching function in module and returns proper response

##### download_handler
- `resolve(link)`
  - Takes in a download data (typically gotten from a scraper_handler resolve)
  ```
  {
    'epNum': 'name of file',
    'sources': [
      'link': 'link',
      'type': 'typically mp4 or iframe',
    ]
  }
  ```

##### info_handler

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

#### Individual Scraper Functions

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

## Contributing

Want to add a downloader or scraper or info collector?
Each module must have
- URL Handeling / a matching_urls variable that looks like this.

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

Refer to [Functions](#Functions) for data formatting

Scrapers should have a couple of functions
- `search`
- `scrape_all_show_sources`
  - scrapes all show details and episodes along with their direct sources

Optionally there can also be
- `_scrape_episode_source`
  - scrapes a single episode's source


Scrapers should be put into the `scrapers` folder

### Adding a downloader
Downloaders are what extract the direct link the the video file or download the file based off a filename.

Downloaders need these functions.
- `download(link, filename)`
  - returns True when download is successful or false if failed.

Downloaders should be put into the `downloaders` folder

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
