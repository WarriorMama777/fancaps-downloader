import argparse
import re
import os
import urllib.request
from bs4 import BeautifulSoup
import concurrent.futures

parser = argparse.ArgumentParser()
parser.add_argument('url', nargs='?', help='Url to start download')
parser.add_argument('--output', type=str, default="Downloads", help='Path of folder')
args = parser.parse_args()

def getUrlType(url):
    match = re.search(r"https://fancaps.net/(.*?)/showimages.php.*?",url)
    if match:
        return "season"
    match = re.search(r"https://fancaps.net/(.*?)/episodeimages.php.*?",url)
    if match:
        return "ep"
    match = re.search(r"https://fancaps.net/movies/MovieImages.php.*?",url)
    if match:
        return 'movie'

def getEpLinks(url):
    links = []
    currentUrl = url
    pageNumber = 1
    name = None

    while currentUrl:
        request = urllib.request.Request(currentUrl, headers={'User-Agent': 'Mozilla/5.0'})
        page = urllib.request.urlopen(request)
        beautifulSoup = BeautifulSoup(page, 'html.parser')

        for link in beautifulSoup.find_all("a", href=re.compile("^.*?/episodeimages.php\?")):
            href = link.get('href')
            if href:
                match = re.search(r"https://fancaps.net/.*?/episodeimages.php\?\d+-(.*?)/", href)
                if match:
                    if not name:
                        name = match.group(1)
                    if name == match.group(1):
                        links.append(href)
        if beautifulSoup.find("a", title="Next Page"):
            pageNumber += 1
            currentUrl = url + f"&page={pageNumber}"
        else:
            currentUrl = None  
    return links

def getPicLink(url):
    links = []
    currentUrl = url
    pageNumber = 1
    alt = None

    match = re.search(r"https://fancaps.net/(.*?)/(.*)", url)
    epType = match.group(1)
    nextUrl = match.group(2)

    if epType == 'tv':
        cdn = 'tvcdn'
    else:
        cdn = 'ancdn'

    while currentUrl:
        request = urllib.request.Request(currentUrl, headers={'User-Agent': 'Mozilla/5.0'})
        page = urllib.request.urlopen(request)
        beautifulSoup = BeautifulSoup(page, "html.parser")  

        for img in beautifulSoup.find_all("img", src=re.compile("^https://"+epType+"thumbs.fancaps.net/")):
            imgSrc = img.get("src")
            imgAlt = img.get("alt")
            if not alt:
                alt = imgAlt
            if alt == imgAlt:
                links.append(imgSrc.replace("https://"+epType+"thumbs.fancaps.net/", "https://"+cdn+".fancaps.net/"))
        next = nextUrl+f"&page={pageNumber + 1}"
        nextPage = beautifulSoup.find("a", href=next)
        if nextPage:
            pageNumber += 1
            currentUrl = url + f"&page={pageNumber}"
        else:
            currentUrl = None
    
    return links

def getMoviePicLink(url):
    links = []
    currentUrl = url
    pageNumber = 1
    alt = None

    match = re.search(r"https://fancaps.net/.*?/(.*)", url)
    nextUrl = match.group(1)

    while currentUrl:
        request = urllib.request.Request(currentUrl, headers={'User-Agent': 'Mozilla/5.0'})
        page = urllib.request.urlopen(request)
        beautifulSoup = BeautifulSoup(page, "html.parser") 

        for img in beautifulSoup.find_all("img", src=re.compile("^https://moviethumbs.fancaps.net/")):
            imgSrc = img.get("src")
            imgAlt = img.get("alt")
            if not alt:
                alt = imgAlt
            if alt == imgAlt:
                links.append(imgSrc.replace("https://moviethumbs.fancaps.net/", "https://mvcdn.fancaps.net/"))
        next = nextUrl+f"&page={pageNumber + 1}"
        nextPage = beautifulSoup.find("a", href=next)
        if nextPage:
            pageNumber += 1
            currentUrl = url + f"&page={pageNumber}"
        else:
            currentUrl = None

    return links

def downloadFile(url, filename):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req) as response, open(filename, 'wb') as output:
        data = response.read()
        output.write(data)

if args.url:
    type = getUrlType(args.url)
    if type == "season":
        for epUrl in getEpLinks(args.url):
            print(f"Current URL scrapping: {epUrl}")

            match = re.search(r"https://fancaps.net/.*?/episodeimages.php\?\d+-([^/]+)/([^/]+)", epUrl)
            if match:
                subfolder = os.path.join(args.output, match.group(1) + "/" + match.group(2))
            else:
                subfolder = args.output
            
            if not os.path.exists(subfolder):
                os.makedirs(subfolder)

            print(f"\t Folder {subfolder} created")
            
            picLinks = getMoviePicLink(epUrl)
            current = 0
            total = len(picLinks)
            for picUrl in picLinks:
                current = current + 1
                with concurrent.futures.ThreadPoolExecutor(max_workers=12) as executor:
                    filename = os.path.join(subfolder, picUrl.split('/')[-1])
                    if not os.path.exists(filename):
                        executor.submit(downloadFile, picUrl, filename)
                        print(f"\t [{current}/{total}] {picUrl} Downloaded")
                    else:
                        print(f"\t [{current}/{total}] {picUrl} already downloaded")


    elif type == "ep":
        print(f"Current URL scrapping: {args.url}")

        match = re.search(r"https://fancaps.net/.*?/episodeimages.php\?\d+-([^/]+)/([^/]+)", args.url)
        if match:
            subfolder = os.path.join(args.output, match.group(1) + "/" + match.group(2))
        else:
            subfolder = args.output
        
        if not os.path.exists(subfolder):
            os.makedirs(subfolder)

        print(f"\t Folder {subfolder} created")

        picLinks = getPicLink(args.url)
        current = 0
        total = len(picLinks)
        for picUrl in picLinks:
            current = current + 1
            with concurrent.futures.ThreadPoolExecutor(max_workers=12) as executor:
                filename = os.path.join(subfolder, picUrl.split('/')[-1])
                if not os.path.exists(filename):
                    executor.submit(downloadFile, picUrl, filename)
                    print(f"\t [{current}/{total}] {picUrl} Downloaded")
                else:
                    print(f"\t [{current}/{total}] {picUrl} already downloaded")


    elif type == "movie":
        print(f"Current URL scrapping: {args.url}")

        match = re.search(r"https://fancaps.net/movies/MovieImages.php\?name=([^/]+)&", args.url)


        if match:
            subfolder = os.path.join(args.output, match.group(1))
        else:
            subfolder = args.output
        
        if not os.path.exists(subfolder):
            os.makedirs(subfolder)

        print(f"\t Folder {subfolder} created")

        picLinks = getMoviePicLink(args.url)
        current = 0
        total = len(picLinks)
        for picUrl in picLinks:
            current = current + 1
            with concurrent.futures.ThreadPoolExecutor(max_workers=12) as executor:
                filename = os.path.join(subfolder, picUrl.split('/')[-1])
                if not os.path.exists(filename):
                    executor.submit(downloadFile, picUrl, filename)
                    print(f"\t [{current}/{total}] {picUrl} Downloaded")
                else:
                    print(f"\t [{current}/{total}] {picUrl} already downloaded")


    else:
        print("Invalid url")
