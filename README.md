# Fancaps Downloader

## About fork

This is a fork from m-patino/fancaps-downloader.
At present, it is just a slight improvement over the original repository.

Changes:
- Added overall error handling
- Added a retry function for errors that occur during crawling and downloading processes to prevent the download from stopping.

__________
`↓ original repo readme`

## About <a name = "about"></a>

This project it's a simple Python script for download screencaps from https://fancaps.net.

## Getting Started <a name = "getting_started"></a>

### Prerequisites

To run this script you need to have Python 3.x installed, the Beautifulsoup4 and tqdm library:

#### python install: 
https://www.python.org/downloads/

#### Beautifulsoup4 and tqdm install: 
```
pip install beautifulsoup4 tqdm
```

## Usage <a name = "usage"></a>

### Arguments
`url`: Url of ressource to download

`--output`: Folder used for download each images

### Url support:
* `https://fancaps.net/{tv|anime}/showimages.php?...`: Url of season page
* `https://fancaps.net/{tv|anime}/episodeimages.php?...`: Url of episode page
* `https://fancaps.net/movies/MovieImages.php?...`: Url of movie page


### Usage exemple:

```
python fancaps-downloader.py --output "Download" URL
```
In this exemple we download all pics of URL into Download folder
 
## TODO List <a name = "todo_list"></a>
- Input txt file for bulk
- Add more arguments

